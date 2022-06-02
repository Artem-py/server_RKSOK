import socket


SERVER_ADDRESS = ('localhost', 8000)
SPECIAL_ORGANS_SERVER_ADDRESS = ('vragi-vezde.to.digital', 51624)
ENCODING = 'UTF-8'
METHODS = ['WRITE', 'GET', 'DELETE']
PROTOCOL_RKSOK = 'RKSOK/1.0'
phonebook_DB = {}


def get_message(socket_to_connect):
    message = ''
    while True:
        chunk = socket_to_connect.recv(128)
        message += chunk.decode(ENCODING)
        if message.endswith('\r\n\r\n'):
            break
    return message


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


def connect_special_organs(message):
    special_organs_socket = socket.create_connection(SPECIAL_ORGANS_SERVER_ADDRESS)
    #request = "AMОЖНА? PKCOK/1.0\r\n" + message

    if method == 'WRITE':
        request = "АМОЖНА? РКСОК/1.0\r\nЗОПИШИ Иван Хмурый РКСОК/1.0\r\n89012345678\r\n\r\n"
    elif method == 'GET':
        request = "АМОЖНА? РКСОК/1.0\r\nОТДОВАЙ Иван Хмурый РКСОК/1.0\r\n89012345678\r\n\r\n"
    else:
        request = "АМОЖНА? РКСОК/1.0\r\nУДОЛИ Иван Хмурый РКСОК/1.0\r\n89012345678\r\n\r\n"

    print(request)
    special_organs_socket.sendall(request.encode(ENCODING))
    response = get_message(special_organs_socket)
    return response


def process_special_organs_response(message, name, method, phone):
    split_message = message.rstrip('\r\n\r\n').split('\r\n')
    permission = split_message[0].split(' ')[0]
    comment = '\r\n'.join(split_message[1:])
    
    positive_template = 'НОРМАЛДЫКС РКСОК/1.0'
    no_such_name_template = 'НИНАШОЛ РКСОК/1.0'
    negative_template = 'НИЛЬЗЯ РКСОК/1.0'

    if permission == 'МОЖНА':
        if method == 'WRITE':
            phonebook_DB[name] = phone
            answer = positive_template + '\r\n' + phone
        elif method == 'GET':
            answer = positive_template + '\r\n' + phonebook_DB[name]  if phonebook_DB.get[name] else no_such_name_template 
        elif method == 'DELETE':
            answer = positive_template if phonebook_DB.pop[name, None] else no_such_name_template
    
    elif permission == 'НИЛЬЗЯ':
        answer = negative_template + comment

    return answer + '\r\n\r\n'


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(SERVER_ADDRESS)
server.listen()

while True:
    print('Waiting for a connection......')

    client_socket, addr = server.accept()
    print('Connected to:', addr)
    client_socket.settimeout(30.0)
    
    try:
        print('Trying to receive a request........')
        client_message = get_message(client_socket)
        print('Message successfully received\nMessage:', client_message)
    except TimeoutError:
        client_socket.sendall("Wrong request. Try again\n".encode(ENCODING))
        client_socket.close()
        print('Failed to receive a message')
        continue
    

    try:
        print('Trying to parse the request..................')
        method, protocol, name, phone_number = get_data_from_request(client_message)
        print(f'Got the data.\nname: {name}\nphone number: {phone_number}\nmethod, protocol: {method, protocol}')
        if not is_request_correct(method, protocol, name):
            raise Exception
        print('Request is correct.........')
    except Exception:
        print('Wrong request, closing connection........')
        client_socket.sendall("Wrong request. Try again\n".encode(ENCODING))
        client_socket.close()
        continue

    print('Connecting to the special organs server................')
    try:
        special_organs_response = connect_special_organs(client_message)
        print("Special organs response is:", special_organs_response)
    except TimeoutError:
        print("Special organs server couldn't process your request")
    
    client_response = process_special_organs_response(special_organs_response, name, method, phone_number)
    client_socket.sendall(client_response.encode(ENCODING))
    client_socket.close()
