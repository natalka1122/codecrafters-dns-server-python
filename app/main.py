import argparse
import asyncio
import signal
import sys
from functools import partial
from typing import Callable, Optional

from app.const import DEFAULT_PORT, HOST
from app.dns_server import DNSServerProtocol
from app.logging_config import get_logger, setup_logging

setup_logging(level="DEBUG", log_dir="logs")
# setup_logging(level="ERROR", log_dir="logs")

logger = get_logger(__name__)


def _signal_handler(sig: signal.Signals, shutdown_event: asyncio.Event) -> None:
    logger.info(f"Received exit signal {sig.name}...")
    shutdown_event.set()


def make_signal_handler(sig: signal.Signals, shutdown_event: asyncio.Event) -> Callable[[], None]:
    return partial(_signal_handler, sig, shutdown_event)


def setup_signal_handlers(shutdown_event: asyncio.Event) -> None:
    """Attach SIGINT and SIGTERM handlers"""
    loop = asyncio.get_running_loop()
    if sys.platform == "win32":  # pragma: no cover
        for sig in (signal.SIGINT, signal.SIGTERM):  # noqa: WPS426
            signal.signal(sig, lambda *_: shutdown_event.set())
    else:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, make_signal_handler(sig, shutdown_event))


def parse_args() -> Optional[tuple[str, int]]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resolver", type=str, help="Replica config")
    args = parser.parse_args()
    resolver = args.resolver
    if resolver is None:
        return None
    ip, port = resolver.split(":")
    return ip, int(port)


async def main() -> None:
    resolver = parse_args()
    logger.info(f"resolver = {resolver}")
    shutdown_event = asyncio.Event()
    setup_signal_handlers(shutdown_event)
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: DNSServerProtocol(resolver), local_addr=(HOST, DEFAULT_PORT)
    )
    try:  # noqa: WPS501
        await shutdown_event.wait()
    finally:
        transport.close()


if __name__ == "__main__":
    with asyncio.Runner() as runner:
        runner.run(main())
