import socket

data1 = (
    b"\xaa\xfb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x0ccodecrafters\x02io\x00\x00\x01\x00\x01"
)
data2 = b"\x17$\x01\x00\x00\x02\x00\x00\x00\x00\x00\x00\x03abc\x11longassdomainname\x03com\x00\x00\x01\x00\x01\x03def\xc0\x10\x00\x01\x00\x01"
# Настройка UDP сокета
udp_ip = "127.0.0.1"
udp_port = 2053

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# for data in [data1, data2]:
for data in [data2]:
    sock.sendto(data, (udp_ip, udp_port))

    print(f"Sent {len(data)} bytes to {udp_ip}:{udp_port}")  # noqa: WPS421
sock.close()
