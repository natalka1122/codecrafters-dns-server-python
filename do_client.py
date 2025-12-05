#!/usr/bin/env python3
import socket
import sys

data1 = (
    b"\xaa\xfb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x0ccodecrafters\x02io\x00\x00\x01\x00\x01"
)
data2 = b"\x17$\x01\x00\x00\x02\x00\x00\x00\x00\x00\x00\x03abc\x11longassdomainname\x03com\x00\x00\x01\x00\x01\x03def\xc0\x10\x00\x01\x00\x01"  # noqa: E501

udp_ip = "172.17.0.4"
udp_port = 2053

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
packets: list[bytes] = [data1, data2]
for data in packets:
    sock.sendto(data, (udp_ip, udp_port))

    sys.stdout.write(f"Sent {len(data)} bytes to {udp_ip}:{udp_port}\n")
    try:
        response, server_address = sock.recvfrom(4096)  # Buffer size of 4096 bytes
    except socket.timeout:
        sys.stderr.write("No response received within timeout period\n")
        continue
    except Exception as e:
        sys.stderr.write(f"Error receiving response: {e}\n")
        continue
    sys.stdout.write(f"Received {len(response)} bytes from {server_address}\n")
    sys.stdout.write(f"Response: {response!r}\n")

sock.close()
