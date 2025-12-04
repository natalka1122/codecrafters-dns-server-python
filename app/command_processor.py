from dataclasses import dataclass

from app.const import RecordClass, RecordType
from app.convert import domainname_to_bytes, int_to_bytes, list_int_to_bytes
from app.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class DnsDatagram:
    qname: list[tuple[str, RecordType, RecordClass]]
    id: int = 1234
    qr: int = 1
    opcode: int = 0
    aa: int = 0
    tc: int = 0
    rd: int = 0
    ra: int = 0
    z: int = 0
    rcode: int = 0
    ancount: int = 0
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
        result += int_to_bytes(self.ancount, 2)
        result += int_to_bytes(self.nscount, 2)
        result += int_to_bytes(self.arcount, 2)
        for qname, qtype, qclass in self.qname:
            result += domainname_to_bytes(qname)
            result += int_to_bytes(qtype, 2)
            result += int_to_bytes(qclass, 2)

        return result


def processor(datagram: bytes) -> bytes:
    result = DnsDatagram(qname=[("codecrafters.io", RecordType.A, RecordClass.IN)]).to_bytes
    logger.info(f"Reply: {len(result)} {result!r}")
    return result
