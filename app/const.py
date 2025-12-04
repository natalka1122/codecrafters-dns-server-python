from enum import IntEnum

HOST = "0.0.0.0"
DEFAULT_PORT = 2053


class RecordType(IntEnum):
    A = 1


class RecordClass(IntEnum):
    IN = 1
