from asyncio import gather, get_running_loop
from collections.abc import Awaitable
from typing import Optional

from app.async_udp_client import AsyncUDPClient
from app.const import (
    DEFAULT_IP,
    OPCODE_QUERY,
    AuthoritativeAnswer,
    QueryResponseIndicator,
    RecordClass,
    RecordType,
    RecursionAvailable,
    RecursionDesired,
    ResponseCode,
)
from app.datagram import DnsDatagram, ListResourceRecord, Question, ResourceRecord
from app.logging_config import get_logger

logger = get_logger(__name__)


async def processor(datagram: bytes, resolver: Optional[tuple[str, int]]) -> bytes:  # noqa: WPS210
    request = DnsDatagram.from_bytes(datagram)

    logger.debug(f"processor: parsed request = {request}")
    if request.opcode != OPCODE_QUERY:
        reply = DnsDatagram(
            id=request.id,
            qr=QueryResponseIndicator.RESPONSE,
            opcode=request.opcode,
            rd=request.rd,
            aa=AuthoritativeAnswer.FALSE,
            ra=RecursionAvailable.FALSE,
            rcode=ResponseCode.NOT_IMPLEMENTED,
            questions=[],
            resource_records=[],
        )
        logger.debug(f"processor: reply = {reply}")
        return reply.to_bytes
    upstream_tasks: list[Awaitable[ListResourceRecord]] = [
        _resolve_upstream(
            qid=request.id, qname=q.qname, qtype=q.qtype, qclass=q.qclass, resolver=resolver
        )
        for q in request.questions
    ]
    upstream_responses: list[ListResourceRecord] = await gather(*upstream_tasks)

    resource_records: ListResourceRecord = []
    for upstream_response in upstream_responses:
        resource_records.extend(upstream_response)
    reply = DnsDatagram(
        id=request.id,
        qr=QueryResponseIndicator.RESPONSE,
        opcode=request.opcode,
        rd=request.rd,
        aa=AuthoritativeAnswer.FALSE,
        ra=RecursionAvailable.FALSE,
        rcode=ResponseCode.NO_ERROR,
        questions=request.questions,
        resource_records=resource_records,
    )
    logger.debug(f"processor: reply = {reply}")
    return reply.to_bytes


async def _resolve_upstream(  # noqa: WPS210
    qid: int,
    qname: bytes,
    qtype: RecordType,
    qclass: RecordClass,
    resolver: Optional[tuple[str, int]],
) -> ListResourceRecord:
    if resolver is None:
        return [
            ResourceRecord(
                rname=qname, rtype=RecordType.A, rclass=RecordClass.IN, rttl=60, rdata=DEFAULT_IP
            )
        ]
    ip, port = resolver
    upstream_request = DnsDatagram(
        id=qid,
        qr=QueryResponseIndicator.QUERY,
        opcode=OPCODE_QUERY,
        aa=AuthoritativeAnswer.FALSE,
        rd=RecursionDesired.FALSE,
        ra=RecursionAvailable.FALSE,
        rcode=ResponseCode.NO_ERROR,
        questions=[Question(qname=qname, qtype=qtype, qclass=qclass)],
        resource_records=[],
    )
    logger.debug(f"_resolve_upstream: upstream_request = {upstream_request}")

    loop = get_running_loop()
    on_response = loop.create_future()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: AsyncUDPClient(upstream_request.to_bytes, on_response), remote_addr=(ip, port)
    )

    upstream_response_bytes = await on_response
    transport.close()
    logger.debug(f"_resolve_upstream: upstream_response_bytes = {upstream_response_bytes}")
    if not isinstance(upstream_response_bytes, bytes):
        raise NotImplementedError
    upstream_response = DnsDatagram.from_bytes(upstream_response_bytes)
    return upstream_response.resource_records
