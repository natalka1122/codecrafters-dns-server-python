from app.const import RecordClass, RecordType
from app.datagram import RR, DnsReply, DnsRequest, Question
from app.logging_config import get_logger

logger = get_logger(__name__)


def processor(datagram: bytes) -> bytes:
    request = DnsRequest.from_bytes(datagram)
    logger.info(f"request = {request}")
    reply = DnsReply(
        id=request.id,
        opcode=request.opcode,
        rd=request.rd,
        rcode=0 if request.opcode == 0 else 4,
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
    )
    logger.info(f"reply = {reply}")
    return reply.to_bytes
