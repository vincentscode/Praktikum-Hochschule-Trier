import socket
import threading

# SETTINGS
HOST = '127.0.0.1'
PORT = 1234
BUFFER_SIZE = 1024

# SOCKET
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# MAIN
while True:
    a = input("")
    if a.strip() != "":
        unsendable = False
        while len(bytes(a, "utf8")) > BUFFER_SIZE:
            a += b'0x00'
        for c in a:
            if c not in [str(i) for i in range(0, 10)] + ["r", "f"]:
                print("Invalid character:", c)
                unsendable = True
                break
        if not unsendable:
            if 'r' in a:
                sock.sendall(bytes(a, "UTF-8"))
                print("rotationVelocity is now", a[1:])
            elif 'f' in a:
                sock.sendall(bytes(a, "UTF-8"))
                print("forwardVelocity is now", a[1:])
            else:
                print("Invalid format.")