from asyncio import (
    BaseTransport,
    DatagramTransport,
    Protocol,
)

from app.command_processor import processor
from app.logging_config import get_logger

logger = get_logger(__name__)


class DNSServerProtocol(Protocol):
    def connection_made(self, transport: BaseTransport) -> None:
        if not isinstance(transport, DatagramTransport):
            raise NotImplementedError
        self.transport: DatagramTransport = transport

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        logger.info(f"datagram_received {data!r}")
        reply = processor(data)
        self.transport.sendto(reply, addr)
        logger.info(f"datagram sent {reply!r}")
