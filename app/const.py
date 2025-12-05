from enum import IntEnum

HOST = "0.0.0.0"
DEFAULT_PORT = 2053
DEFAULT_IP = b"\x08\x08\x08\x08"


OPCODE_QUERY = 0


class QueryResponseIndicator(IntEnum):
    QUERY = 0
    RESPONSE = 1


class RecordType(IntEnum):
    A = 1


class RecordClass(IntEnum):
    IN = 1


class AuthoritativeAnswer(IntEnum):
    TRUE = 1
    FALSE = 0


class RecursionDesired(IntEnum):
    TRUE = 1
    FALSE = 0


class RecursionAvailable(IntEnum):
    TRUE = 1
    FALSE = 0


class ResponseCode(IntEnum):
    NO_ERROR = 0
    NOT_IMPLEMENTED = 4
