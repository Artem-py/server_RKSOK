"""Contains functions to work with clients' requests

"""
import asyncio
from dataclasses import dataclass

from exceptions import DisconnectionError, ConnectionError, WrongRequestError


ENCODING = 'UTF-8'
METHODS = ['ОТДОВАЙ', 'ЗОПИШИ', 'УДОЛИ']
PROTOCOL_RKSOK = 'РКСОК/1.0'


@dataclass(slots=True, frozen=True)
class Request:
    method: str
    protocol: str
    name: str
    contact_info: str
    full_text: str


async def get_request(reader: asyncio.StreamReader) -> Request:
    """Receives client's request, processes it and, if request is correct,
    returns Request object
    
    """
    request = await asyncio.wait_for(get_message(reader), timeout=60)
    method, protocol, name, contact_info = get_data_from_request(request)
    return Request(method=method, name=name, protocol=protocol, 
                   contact_info=contact_info, full_text=request)


async def get_message(reader: asyncio.StreamReader) -> str:
    """Takes an asyncio reader object, receives client's message and returns it in string format.
    Raises ConnectionError if an error occurs during reading (such as TimeoutError) or client gets disconnected.
    
    """
    try:
        message = ''
        while True:
            chunk = await reader.read(128)
            if not chunk:
                raise DisconnectionError('Client has closed the connection')
            message += chunk.decode(ENCODING)
            if message.endswith('\r\n\r\n'):
                break
        return message
    except (DisconnectionError, asyncio.TimeoutError) as e:
        raise ConnectionError('Error on the client side')


def get_data_from_request(request: str) -> tuple:
    """Parses client's message and checks if the message format is correct
    
    """
    split_message = request.rstrip('\r\n\r\n').split('\r\n')
    head_line = split_message[0].split(' ')
    method = head_line[0]
    protocol = head_line[-1]
    name = ' '.join(head_line[1:-1])
    phone_number = '\r\n'.join(split_message[1:])

    if is_request_correct(method, name, protocol):
        return method, protocol, name, phone_number


def is_request_correct(method: str, name: str, protocol: str) -> bool:
    """Returns True if response complies with all the protocol syntactic requirements, otherwise raises WrongRequestError exception
    
    """
    if method not in METHODS or len(name) > 30 or protocol != PROTOCOL_RKSOK:
        raise WrongRequestError('Could not parse the request')
    return True
