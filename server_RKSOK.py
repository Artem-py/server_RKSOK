import asyncio
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


class ConnectionError(Exception):
    pass

class  MessageParsingError(Exception):
    pass


async def get_message(reader):
    message = ''
    while True:
        chunk = await reader.read(128)
        if not chunk:
            raise ConnectionError
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


async def connect_special_organs(message):
    reader, writer = await asyncio.open_connection(*SPECIAL_ORGANS_SERVER_ADDRESS)
    writer.write(message.encode(ENCODING))
    response = await get_message(reader)
    writer.close()
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


async def handle_connection(reader, writer):
    addr = writer.get_extra_info('peername')
    logger_name = 'main.ip_{}_port_{}'.format(*addr)
    logger = logging.getLogger(logger_name)
    logger.info('Connection accepted')

    logger.debug('Trying to receive a message from the client')
    try: 
        client_message = await asyncio.wait_for(get_message(reader), timeout=60)
        logger.debug('Message received:\n{!r}'.format(client_message))
    except (asyncio.TimeoutError, ConnectionError) as ex:
        logger.exception(ex)
        logger.debug('Closing the connection')
        writer.close()
        await writer.wait_closed()
        return
        
    logger.debug('Trying to parse the request')
    try:
        method, protocol, name, phone_number = get_data_from_request(client_message)
        logger.debug('Request is correct.\r\nGot the data.\r\nname: {!r}\r\nphone number: {!r}\r\n\
method, protocol: {!r}, {!r}'.format(name, phone_number, method, protocol))
    except MessageParsingError:
        logger.exception('Could not parse the request')
        writer.write('Wrong request, try again'.encode(ENCODING))
        await writer.drain()
        logger.debug('Closing the connection')
        writer.close()
        await writer.wait_closed()
        return

    message_to_check = 'АМОЖНА? РКСОК/1.0\r\n' + client_message
    logger.debug('Connecting to the special organs server, message is:\r\n{!r}'.format(message_to_check))
    try: 
        special_organs_response = await connect_special_organs(message_to_check)
        logger.debug('special organs responce is:\n{!r}'.format(special_organs_response))
    except ConnectionError:
        logger.exception('Failed to connect special organs server')
        writer.write('Sorry, cannot process your request. Try again later'.encode(ENCODING))
        await writer.drain()
        logger.debug('Closing the connection')
        writer.close()
        await writer.wait_closed()
        return

    client_response = process_special_organs_response(special_organs_response, name, method, phone_number)
    logger.debug('Sending the response to the client, response is:\r\n{!r}'.format(client_response))
    writer.write(client_response.encode(ENCODING))
    await writer.drain()
    logger.info('Closing the connection')
    writer.close()
    await writer.wait_closed()
    return


async def main():
    server = await asyncio.start_server(handle_connection, *SERVER_ADDRESS)
    logger.debug('Starting up on {} port {}'.format(*SERVER_ADDRESS))

    async with server:
        await server.serve_forever()


asyncio.run(main())