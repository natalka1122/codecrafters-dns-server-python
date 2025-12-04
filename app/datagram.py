from dataclasses import dataclass
from typing import NamedTuple

from app.const import RecordClass, RecordType
from app.convert import (
    domainname_to_bytes,
    int_to_bytes,
    ip_to_bytes,
    list_int_to_bytes,
    read_next_domainname,
    read_next_int,
    read_next_list_int,
)


class Question(NamedTuple):
    qname: bytes
    qtype: RecordType
    qclass: RecordClass


class ResourceRecord(NamedTuple):
    rname: bytes
    rtype: RecordType
    rclass: int
    rttl: int
    rdata: str


@dataclass
class DnsDatagram:
    questions: list[Question]
    resource_records: list[ResourceRecord]
    id: int
    qr: int = 1
    opcode: int = 0
    aa: int = 0
    tc: int = 0
    rd: int = 0
    ra: int = 0
    z: int = 0
    rcode: int = 0
    nscount: int = 0
    arcount: int = 0

    @property
    def to_bytes(self) -> bytes:
        result = int_to_bytes(self.id, 2)
        result += list_int_to_bytes(
            [
                (self.qr, 1),
                (self.opcode, 4),
                (self.aa, 1),
                (self.tc, 1),
                (self.rd, 1),
                (self.ra, 1),
                (self.z, 3),
                (self.rcode, 4),
            ],
        )
        result += int_to_bytes(len(self.questions), 2)
        result += int_to_bytes(len(self.resource_records), 2)
        result += int_to_bytes(self.nscount, 2)
        result += int_to_bytes(self.arcount, 2)
        for question in self.questions:
            result += domainname_to_bytes(question.qname)
            result += int_to_bytes(question.qtype, 2)
            result += int_to_bytes(question.qclass, 2)
        for record in self.resource_records:
            result += domainname_to_bytes(record.rname)
            result += int_to_bytes(record.rtype, 2)
            result += int_to_bytes(record.rclass, 2)
            result += int_to_bytes(record.rttl, 4)
            result += int_to_bytes(4, 4)  # hardcoded 4-bytes for ipv4
            result += ip_to_bytes(record.rdata)
        return result

    @classmethod
    def from_bytes(cls, data: bytes) -> "DnsDatagram":  # noqa: WPS210
        data, packet_id = read_next_int(data, 2)  # noqa: WPS204
        data, pack = read_next_list_int(data, [1, 4, 1, 1, 1])
        qr, opcode, aa, tc, rd = pack  # noqa: WPS236
        data, pack = read_next_list_int(data, [1, 3, 4])
        ra, z, rcode = pack
        data, qdcount = read_next_int(data, 2)
        data, ancount = read_next_int(data, 2)
        data, nscount = read_next_int(data, 2)
        data, arcount = read_next_int(data, 2)
        questions: list[Question] = []
        for _ in range(qdcount):
            data, qname = read_next_domainname(data)
            data, qtype = read_next_int(data, 2)
            data, qclass = read_next_int(data, 2)
            questions.append(
                Question(qname=qname, qtype=RecordType(qtype), qclass=RecordClass(qclass))
            )
        return DnsDatagram(  # noqa: WPS221
            id=packet_id,
            qr=qr,
            opcode=opcode,
            aa=aa,
            tc=tc,
            rd=rd,
            ra=ra,
            z=z,
            rcode=rcode,
            questions=questions,
            resource_records=[],
        )
