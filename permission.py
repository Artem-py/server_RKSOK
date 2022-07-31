"""Contains functions to work with Special Organs server

"""
import asyncio
from dataclasses import dataclass

from request import Request
from exceptions import SpecialOrgansServerError, DisconnectionError
from request import get_message


ENCODING = 'UTF-8'
SPECIAL_ORGANS_SERVER_ADDRESS = ('vragi-vezde.to.digital', 51624)


async def get_permission(request: Request) -> str:
    """Sends request to the Special Organs Server and returns its response
    as Permission object
    
    """
    special_organs_response = await connect_special_organs(request.full_text)
    return special_organs_response


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


    