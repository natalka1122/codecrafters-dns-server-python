from dataclasses import dataclass
from typing import NamedTuple

from app.const import RecordClass, RecordType
from app.convert import (
    domainname_to_bytes,
    int_to_bytes,
    ip_to_bytes,
    list_int_to_bytes,
)
from app.logging_config import get_logger

logger = get_logger(__name__)


class Question(NamedTuple):
    qname: str
    qtype: RecordType
    qclass: RecordClass


class RR(NamedTuple):
    rname: str
    rtype: RecordType
    rclass: int
    rttl: int
    rdata: str


@dataclass
class DnsDatagram:
    qname: list[Question]
    rr: list[RR]
    id: int = 1234
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
        logger.info(f"DnsDatagram = {self}")
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
        result += int_to_bytes(len(self.qname), 2)
        result += int_to_bytes(len(self.rr), 2)
        result += int_to_bytes(self.nscount, 2)
        result += int_to_bytes(self.arcount, 2)
        for question in self.qname:
            result += domainname_to_bytes(question.qname)
            result += int_to_bytes(question.qtype, 2)
            result += int_to_bytes(question.qclass, 2)
        for record in self.rr:
            result += domainname_to_bytes(record.rname)
            result += int_to_bytes(record.rtype, 2)
            result += int_to_bytes(record.rclass, 2)
            result += int_to_bytes(record.rttl, 4)
            result += int_to_bytes(4, 4)  # 4-bytes for ipv4
            result += ip_to_bytes(record.rdata)

        return result


def processor(datagram: bytes) -> bytes:
    result = DnsDatagram(
        qname=[Question(qname="codecrafters.io", qtype=RecordType.A, qclass=RecordClass.IN)],
        rr=[
            RR(
                rname="codecrafters.io",
                rtype=RecordType.A,
                rclass=RecordClass.IN,
                rttl=60,
                rdata="8.8.8.8",
            )
        ],
    ).to_bytes
    logger.info(f"Reply: {len(result)} {result!r}")
    return result
