from asyncio import (
    BaseTransport,
    DatagramTransport,
    Protocol,
    Runner,
    get_running_loop,
    sleep,
)

from app.const import DEFAULT_PORT, HOST
from app.logging_config import get_logger, setup_logging

setup_logging(level="DEBUG", log_dir="logs")
# setup_logging(level="ERROR", log_dir="logs")

logger = get_logger(__name__)


class DNSServerProtocol(Protocol):
    def connection_made(self, transport: BaseTransport) -> None:
        if not isinstance(transport, DatagramTransport):
            raise NotImplementedError
        self.transport: DatagramTransport = transport

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        logger.info(f"datagram_received {data!r}")
        self.transport.sendto(data, addr)


async def main() -> None:
    logger.debug("Starting DNS server...")
    loop = get_running_loop()

    transport, _ = await loop.create_datagram_endpoint(
        DNSServerProtocol, local_addr=(HOST, DEFAULT_PORT)
    )
    try:  # noqa: WPS501
        await sleep(float("inf"))
    finally:
        transport.close()


if __name__ == "__main__":
    with Runner() as runner:
        runner.run(main())
