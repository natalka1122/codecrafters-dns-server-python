def int_to_bytes(data: int, size: int) -> bytes:
    if data < 0:
        raise ValueError("data must be non-negative")
    if data >= (1 << (size * 8)):
        raise ValueError(f"data too large to fit in {size} bytes")

    return data.to_bytes(size)


def bytes_to_int(data: bytes) -> int:
    return int.from_bytes(data)


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


def ip_to_bytes(ip: str) -> bytes:
    result = b""
    for num in ip.split("."):  # noqa: WPS519
        result += int_to_bytes(int(num), 1)
    return result


def read_next_int(data: bytes, size: int) -> tuple[bytes, int]:
    if len(data) < size:
        raise NotImplementedError
    result = bytes_to_int(data[:size])
    return data[size:], result


def read_next_list_int(  # noqa: WPS210
    data: bytes, sizes: list[int]
) -> tuple[bytes, tuple[int, ...]]:
    total_bits = sum(sizes)
    expected_bytes = total_bits // 8

    if total_bits % 8 != 0:
        raise ValueError("total bits must be divisible by 8")

    if len(data) < expected_bytes:
        raise ValueError(f"data length {len(data)} doesn't match expected {expected_bytes} bytes")

    bit_string = "".join(format(byte, "08b") for byte in data)

    result: list[int] = []
    bit_position = 0
    for bit_size in sizes:
        bit_chunk = bit_string[bit_position : bit_position + bit_size]
        value = int(bit_chunk, 2)
        result.append(value)
        bit_position += bit_size

    return data[: expected_bytes + 1], tuple(result)
