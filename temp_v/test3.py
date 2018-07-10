import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", 12223))
sock.listen(1)

while True:
	conn, addr = sock.accept()
	print(conn, addr, "connected")
