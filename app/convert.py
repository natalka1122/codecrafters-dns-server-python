def int_to_bytes(data: int, size: int) -> bytes:
    if data < 0:
        raise ValueError("data must be non-negative")
    if data >= (1 << (size * 8)):
        raise ValueError(f"data too large to fit in {size} bytes")

    return data.to_bytes(size, byteorder="big")


def list_int_to_bytes(data: list[tuple[int, int]]) -> bytes:  # noqa: WPS210
    bit_string = ""
    for value, bit_size in data:
        if value < 0:
            raise ValueError(f"all values must be non-negative, got {value}")
        if value >= (1 << bit_size):
            raise ValueError(f"value {value} too large for {bit_size} bits")

        bit_string += format(value, f"0{bit_size}b")

    if len(bit_string) % 8 != 0:
        raise NotImplementedError

    result: bytes = b""
    for i in range(0, len(bit_string), 8):
        byte_chunk = bit_string[i : i + 8]
        result += int(byte_chunk, 2).to_bytes(1)

    return result


def domainname_to_bytes(domainname: str) -> bytes:
    result = b""
    for label in domainname.split(".") + [""]:  # noqa: WPS519
        result += int_to_bytes(len(label), 1) + label.encode()
    return result
