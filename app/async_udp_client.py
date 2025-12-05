from asyncio import BaseTransport, DatagramProtocol, DatagramTransport, Future

from app.logging_config import get_logger

logger = get_logger(__name__)


class AsyncUDPClient(DatagramProtocol):
    def __init__(self, data: bytes, on_response: Future[bytes]):
        self.data: bytes = data
        self.on_response = on_response

    def connection_made(self, transport: BaseTransport) -> None:
        if not isinstance(transport, DatagramTransport):
            logger.error(
                f"AsyncUDPClient.connection_made: self.transport = {type(transport)} {transport}"
            )
            raise NotImplementedError
        self.transport = transport
        logger.debug(
            f"AsyncUDPClient.connection_made: sending {len(self.data)} bytes {self.data!r}"
        )
        self.transport.sendto(self.data, None)

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        if not self.on_response.done():
            self.on_response.set_result(data)
        self.transport.close()

    def error_received(self, exc: Exception) -> None:
        logger.error(f"AsyncUDPClient.error_received: {type(exc)} {exc}")
        if not self.on_response.done():
            self.on_response.set_exception(exc)
