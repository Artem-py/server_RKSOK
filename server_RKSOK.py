import socket
import json

import logging
import logging.config
from log_settings import logger_config


logging.config.dictConfig(logger_config)
logger = logging.getLogger('main')


SERVER_ADDRESS = ('localhost', 8000)
SPECIAL_ORGANS_SERVER_ADDRESS = ('vragi-vezde.to.digital', 51624)
ENCODING = 'UTF-8'
METHODS = ['WRITE', 'GET', 'DELETE']
PROTOCOL_RKSOK = 'RKSOK/1.0'


class MessageParsingError(Exception):
    pass


def get_message(connection):
    message = ''
    while True:
        chunk = connection.recv(128)
        if not chunk:
            connection.close()
            return None
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

    if method in METHODS and len(name) <= 30 and protocol == PROTOCOL_RKSOK:
        return method, protocol, name, phone_number
    else: raise MessageParsingError


def connect_special_organs(message):
    special_organs_socket = socket.create_connection(SPECIAL_ORGANS_SERVER_ADDRESS)
    #request = "AMОЖНА? PKCOK/1.0\r\n" + message

    if method == 'WRITE':
        request = "АМОЖНА? РКСОК/1.0\r\nЗОПИШИ Иван Хмурый РКСОК/1.0\r\n89012345678\r\n\r\n"
    elif method == 'GET':
        request = "АМОЖНА? РКСОК/1.0\r\nОТДОВАЙ Иван Хмурый РКСОК/1.0\r\n89012345678\r\n\r\n"
    else:
        request = "АМОЖНА? РКСОК/1.0\r\nУДОЛИ Иван Хмурый РКСОК/1.0\r\n89012345678\r\n\r\n"

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

    with open('phonebook_DB.json', 'r') as f:
        phonebook_DB = json.load(f)

    if permission == 'МОЖНА':
        if method == 'WRITE':
            phonebook_DB[name] = phone
            answer = positive_template + '\r\n' + phone
        elif method == 'GET':
            answer = positive_template + '\r\n' + phonebook_DB[name]  if name in phonebook_DB else no_such_name_template 
        elif method == 'DELETE':
            answer = positive_template if name in phonebook_DB else no_such_name_template
            del phonebook_DB[name]
    
    elif permission == 'НИЛЬЗЯ':
        answer = negative_template + comment

    with open('phonebook_DB.json', 'w') as f:    
        json.dump(phonebook_DB, f)
       
    return answer + '\r\n\r\n'


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(SERVER_ADDRESS)
server.listen()

while True:
    logger.info('Waiting for connection')

    client_socket, addr = server.accept()
    logger.debug(f'Connected to: {addr}')
    client_socket.settimeout(30.0)
    
    try:
        logger.debug('Trying to receive a request')
        client_message = get_message(client_socket)
        if not client_message:
            logger.info('User disconnected')
            continue
        logger.info(f'Message successfully received\nMessage: {client_message}')
    except TimeoutError:
        logger.exception('Timeout error occured')
        client_socket.sendall("Wrong request. Try again\n".encode(ENCODING))
        client_socket.close()
        continue
    

    try:
        logger.debug('Trying to parse request')
        method, protocol, name, phone_number = get_data_from_request(client_message)
        logger.info(f'Request is correct.........\nGot the data.\nname: {name}\nphone number: {phone_number}\nmethod, protocol: {method, protocol}')
    except MessageParsingError:
        logger.exception('Could not parse request')
        client_socket.sendall("Wrong request. Try again\n".encode(ENCODING))
        client_socket.close()
        continue

    try:
        logger.debug('Connecting to the special organs server')
        special_organs_response = connect_special_organs(client_message)
        logger.debug(f"Special organs response is: {special_organs_response}")
    except TimeoutError:
        logger.exception("Special organs server couldn't process your request")
    
    client_response = process_special_organs_response(special_organs_response, name, method, phone_number)
    logger.debug(f'Sending a response......\r\n{client_response}')
    client_socket.sendall(client_response.encode(ENCODING))
    client_socket.close()
    logger.info('Connection has been successfully closed!\n' + '-' * 100 + '\r\n')
