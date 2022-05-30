import socket


server_addres = ('localhost', 8000)
ENCODING = 'UTF-8'
phonebook_DB = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(server_addres)
server.listen()

while True:

    client_socket, addr = server.accept()
    message = ''

    while True:
        chunk = client_socket.recv(128)
        message += chunk.decode(ENCODING)
        if message.endswith('\r\n\r\n'):
            break
    print(message)
    client_socket.close()