"""Contains functions to work with Special Organs server

"""
import asyncio
from dataclasses import dataclass

from request import Request
from exceptions import SpecialOrgansServerError, DisconnectionError
from request import get_message


ENCODING = 'UTF-8'
SPECIAL_ORGANS_SERVER_ADDRESS = ('vragi-vezde.to.digital', 51624)


@dataclass(slots=True, frozen=True)
class Permission:
    permit: str
    comment: str
    full_text: str


async def get_permission(request: Request) -> Permission:
    """Sends request to the Special Organs Server and returns its response
    as Permission object
    
    """
    special_organs_response = await connect_special_organs(Request.full_text)
    permit, comment = process_special_organs_response(special_organs_response)
    return Permission(permit=permit, comment=comment, full_text=special_organs_response)


async def connect_special_organs(message: str) -> str:
    """Connects to the Special Organs Server in order to get permission to process client's message.
    Returns string format message if server responses, otherwise raises SpecialOrgansServerError Error
    
    """
    try:
        check_request_headline = 'АМОЖНА? РКСОК/1.0\r\n'
        message_to_check = check_request_headline + message
        reader, writer = await asyncio.open_connection(*SPECIAL_ORGANS_SERVER_ADDRESS)
        writer.write(message_to_check.encode(ENCODING))
        response = await asyncio.wait_for(get_message(reader), timeout=30)
        writer.close()
        return response
    except (asyncio.TimeoutError, DisconnectionError):
        raise SpecialOrgansServerError('Failed to connect special organs server')


def process_special_organs_response(response: str) -> tuple:
    """Forms a message to send to client based on the Special Organs Response. 
    In case the Special Organs Response is positive, goes to the PhoneBook database to get the required information.
    Returns message in string format
    
    """
    split_message = response.rstrip('\r\n\r\n').split('\r\n')
    permit = split_message[0].split(' ')[0]
    comment = '\r\n'.join(split_message[1:])
    return permit, comment
    