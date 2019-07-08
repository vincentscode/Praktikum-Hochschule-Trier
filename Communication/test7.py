import socket
from _thread import *

# SETTINGS
HOST = ''
PORT = 2345
BUFFER_SIZE = 1024

# SOCKET
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(2)

rotation = 456
forward = 123

def recv():
	global forward, rotation
	while True:
		a = input("> ")
		if a.strip() != "":
			unsendable = False
			while len(bytes(a, "utf8")) > BUFFER_SIZE:
				a += b'0x00'
			for c in a:
				if c not in [str(i) for i in range(0, 10)] + ["r", "f", "-"]:
					print("Invalid character:", c)
					unsendable = True
					break
			if not unsendable:
				if 'r' in a:
					rotation = a.replace("r", "")
					print("rotationVelocity is now", a[1:])
				elif 'f' in a:
					forward = a.replace("f", "")
					print("forwardVelocity is now", a[1:])
				else:
					print("Invalid format.")

start_new_thread(recv, ())

# MAIN
while True:
	conn, addr = sock.accept()
	conn.sendall(bytes("r{}/f{}\n".format(rotation, forward), "utf8"))
