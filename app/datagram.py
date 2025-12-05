from dataclasses import dataclass
from typing import NamedTuple

from app.const import (
    AuthoritativeAnswer,
    QueryResponseIndicator,
    RecordClass,
    RecordType,
    RecursionAvailable,
    RecursionDesired,
    ResponseCode,
)
from app.convert import (
    domainname_to_bytes,
    int_to_bytes,
    ip_to_bytes,
    list_int_to_bytes,
    read_next_domainname,
    read_next_int,
    read_next_ip,
    read_next_list_int,
    skip_next_bytes,
)


class Question(NamedTuple):
    qname: bytes
    qtype: RecordType
    qclass: RecordClass


ListQuestion = list[Question]


class ResourceRecord(NamedTuple):
    rname: bytes
    rtype: RecordType
    rclass: int
    rttl: int
    rdata: bytes


ListResourceRecord = list[ResourceRecord]


@dataclass
class DnsDatagram:
    id: int
    qr: QueryResponseIndicator
    opcode: int
    aa: AuthoritativeAnswer
    rd: RecursionDesired
    ra: RecursionAvailable
    rcode: ResponseCode
    questions: ListQuestion
    resource_records: ListResourceRecord

    @property
    def to_bytes(self) -> bytes:
        result = int_to_bytes(self.id, 2)
        result += list_int_to_bytes(
            [
                (self.qr, 1),
                (self.opcode, 4),
                (0, 1),  # AA
                (0, 1),  # TC
                (self.rd, 1),
                (self.ra, 1),
                (0, 3),  # Z
                (self.rcode, 4),
            ],
        )
        result += int_to_bytes(len(self.questions), 2)
        result += int_to_bytes(len(self.resource_records), 2)
        result += int_to_bytes(0, 2)  # NSCOUNT
        result += int_to_bytes(0, 2)  # ARCOUNT
        for question in self.questions:
            result += domainname_to_bytes(question.qname)
            result += int_to_bytes(question.qtype, 2)
            result += int_to_bytes(question.qclass, 2)
        for record in self.resource_records:
            result += domainname_to_bytes(record.rname)
            result += int_to_bytes(record.rtype, 2)
            result += int_to_bytes(record.rclass, 2)
            result += int_to_bytes(record.rttl, 4)
            result += ip_to_bytes(record.rdata)
        return result

    @classmethod
    def from_bytes(cls, data: bytes) -> "DnsDatagram":  # noqa: WPS210
        orig_data = data
        data, packet_id = read_next_int(data, 2)  # noqa: WPS204
        data, pack = read_next_list_int(data, [1, 4, 1, 1, 1, 1, 3, 4])  # noqa: WPS221
        # QR, OPCODE, AA, TC, RD, RA, Z, RCODE = pack
        qr = pack[0]
        opcode = pack[1]
        rd = pack[4]
        rcode = pack[7]
        data, qdcount = read_next_int(data, 2)
        data, ancount = read_next_int(data, 2)
        data = skip_next_bytes(data, 2)  # nscount
        data = skip_next_bytes(data, 2)  # arcount
        questions: ListQuestion = []
        for _ in range(qdcount):
            data, qname = read_next_domainname(data, orig_data)
            data, qtype = read_next_int(data, 2)
            data, qclass = read_next_int(data, 2)
            questions.append(
                Question(qname=qname, qtype=RecordType(qtype), qclass=RecordClass(qclass))
            )
        resource_records: ListResourceRecord = []
        for _ in range(ancount):
            data, rname = read_next_domainname(data, orig_data)
            data, rtype = read_next_int(data, 2)
            data, rclass = read_next_int(data, 2)
            data, rttl = read_next_int(data, 4)
            data, rdata = read_next_ip(data)
            resource_records.append(
                ResourceRecord(
                    rname=rname,
                    rtype=RecordType(rtype),
                    rclass=RecordClass(rclass),
                    rttl=rttl,
                    rdata=rdata,
                )
            )
        return DnsDatagram(  # noqa: WPS221
            id=packet_id,
            qr=QueryResponseIndicator(qr),
            opcode=opcode,
            aa=AuthoritativeAnswer.FALSE,
            rd=RecursionDesired(rd),
            ra=RecursionAvailable.FALSE,
            rcode=ResponseCode(rcode),
            questions=questions,
            resource_records=resource_records,
        )
