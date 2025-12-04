import socket

data = b"\xaa\xfb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x0ccodecrafters\x02io\x00\x00\x01\x00\x01"

# Настройка UDP сокета
udp_ip = "127.0.0.1"
udp_port = 2053

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(data, (udp_ip, udp_port))

print(f"Sent {len(data)} bytes to {udp_ip}:{udp_port}")  # noqa: WPS421
sock.close()
