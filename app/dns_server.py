from asyncio import (
    BaseTransport,
    DatagramProtocol,
    DatagramTransport,
    create_task,
)
from typing import Optional

from app.command_processor import processor
from app.logging_config import get_logger

logger = get_logger(__name__)


class DNSServerProtocol(DatagramProtocol):
    def __init__(self, resolver: Optional[tuple[str, int]]) -> None:
        self.resolver = resolver

    def connection_made(self, transport: BaseTransport) -> None:
        if not isinstance(transport, DatagramTransport):
            raise NotImplementedError
        self.transport: DatagramTransport = transport

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        logger.debug(f"DNSServerProtocol.datagram_received: from {addr} received {data!r}")
        create_task(self.process_and_reply(data, addr))

    async def process_and_reply(self, data: bytes, addr: tuple[str, int]) -> None:
        reply = await processor(data, self.resolver)
        self.transport.sendto(reply, addr)
        logger.debug(f"DNSServerProtocol.process_and_reply: to {addr} sent {reply!r}")
