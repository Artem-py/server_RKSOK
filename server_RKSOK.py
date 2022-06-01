import socket


server_addres = ('localhost', 8000)
ENCODING = 'UTF-8'
METHODS = ['WRITE', 'READ', 'DELETE']
PROTOCOL_RKSOK = 'RKSOK/1.0'
phonebook_DB = {}


def get_data_from_request(request_message):
    split_message = request_message.rstrip('\r\n\r\n').split('\r\n')
    head_line = split_message[0].split(' ')
    method = head_line[0]
    protocol = head_line[-1]
    name = ' '.join(head_line[1:-1])
    phone_number = '\r\n'.join(split_message[1:])
    return method, protocol, name, phone_number


def is_request_correct(method, protocol, name):
    return method in METHODS and len(name) <= 30 and protocol == PROTOCOL_RKSOK


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(server_addres)
server.listen()

while True:
    print('Waiting for a connection......')

    client_socket, addr = server.accept()
    client_socket.settimeout(30.0)
    
    message = ''
    try:
        while True:
            chunk = client_socket.recv(128)
            message += chunk.decode(ENCODING)
            if message.endswith('\r\n\r\n'):
                break
        print(message)
    except TimeoutError:
        client_socket.sendall("Wrong request. Try again\n".encode(ENCODING))
        client_socket.close()
        continue

    try:
        method, protocol, name, phone_number = get_data_from_request(message)
        ready_to_process = is_request_correct(method, protocol, name)
    except Exception:
        client_socket.sendall("Wrong request. Try again\n".encode(ENCODING))
        client_socket.close()

print(phone_number)

    