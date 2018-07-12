import socket

ip = ''
port = 1234
buffer_size = 4096

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((ip, port))
server_socket.listen(1)

print("Waiting for clients.")

while True:
    conn, addr = server_socket.accept()
    print(addr, "connected.")