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


def domainname_to_bytes(domainname: bytes) -> bytes:
    result = b""
    for label in domainname.split(b".") + [b""]:  # noqa: WPS519
        result += int_to_bytes(len(label), 1) + label
    return result


def _read_next_label(data: bytes) -> tuple[bytes, bytes]:
    data, length = read_next_int(data, 1)
    result = data[:length]
    return data[length:], result


def read_next_domainname(data: bytes, orig_data: bytes, _depth: int = 0) -> tuple[bytes, bytes]:
    if _depth > 2:
        raise ValueError("DNS compression depth limit exceeded (possible cycle)")
    result: list[bytes] = []
    while len(data) > 0 and data[0] != 0:
        if data[0] & 0xC0 == 0xC0:  # compression
            offset = ((data[0] & 0x3F) << 8) | data[1]
            _, compressed_part = read_next_domainname(orig_data[offset:], orig_data, _depth + 1)
            result.append(compressed_part)
            return data[2:], b".".join(result)
        data, label = _read_next_label(data)
        result.append(label)
    return data[1:], b".".join(result)


def ip_to_bytes(ip: bytes) -> bytes:
    result = int_to_bytes(len(ip), 2)
    result += ip
    return result


def read_next_ip(data: bytes) -> tuple[bytes, bytes]:
    data, length = read_next_int(data, 2)
    return data[length:], data[:length]


def read_next_int(data: bytes, size: int) -> tuple[bytes, int]:
    if len(data) < size:
        raise NotImplementedError
    result = bytes_to_int(data[:size])
    return data[size:], result


def skip_next_bytes(data: bytes, size: int) -> bytes:
    if len(data) < size:
        raise NotImplementedError
    return data[size:]


def read_next_list_int(  # noqa: WPS210
    data: bytes, sizes: list[int]
) -> tuple[bytes, tuple[int, ...]]:
    total_bits = sum(sizes)
    expected_bytes = total_bits // 8

    if total_bits % 8 != 0:
        raise ValueError("total bits must be divisible by 8")

    if len(data) < expected_bytes:
        raise ValueError(f"data length {len(data)} doesn't match expected {expected_bytes} bytes")

    bit_string = "".join(format(byte, "08b") for byte in data[:expected_bytes])  # noqa: WPS221

    result: list[int] = []
    bit_position = 0
    for bit_size in sizes:
        bit_chunk = bit_string[bit_position : bit_position + bit_size]
        value = int(bit_chunk, 2)
        result.append(value)
        bit_position += bit_size

    return data[expected_bytes:], tuple(result)
