from app.datagram import DnsDatagram, ResourceRecord
from app.logging_config import get_logger

logger = get_logger(__name__)


def processor(datagram: bytes) -> bytes:
    request = DnsDatagram.from_bytes(datagram)
    logger.info(f"request = {request}")
    resource_records = [
        ResourceRecord(
            rname=q.qname,
            rtype=q.qtype,
            rclass=q.qclass,
            rttl=60,
            rdata="8.8.8.8",
        )
        for q in request.questions
    ]
    reply = DnsDatagram(
        id=request.id,
        opcode=request.opcode,
        rd=request.rd,
        rcode=0 if request.opcode == 0 else 4,
        questions=request.questions,
        resource_records=resource_records,
    )
    logger.info(f"reply = {reply}")
    return reply.to_bytes
