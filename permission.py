"""Contains functions to work with Special Organs server

"""
import asyncio
from dataclasses import dataclass

from request import Request
from exceptions import SpecialOrgansServerError, ConnectionError
from request import get_message


ENCODING = 'UTF-8'
SPECIAL_ORGANS_SERVER_ADDRESS = ('vragi-vezde.to.digital', 51624)
CHECK_REQUEST_HEADLINE = 'АМОЖНА? РКСОК/1.0\r\n'


async def get_permission(request: Request) -> str:
    """Sends request to the Special Organs Server and returns its response
    in string format
    
    """
    try:
        message_to_check = CHECK_REQUEST_HEADLINE + request.full_text
        reader, writer = await asyncio.open_connection(*SPECIAL_ORGANS_SERVER_ADDRESS)
        writer.write(message_to_check.encode(ENCODING))
        special_organs_response = await asyncio.wait_for(get_message(reader), timeout=30)
        writer.close()
        return special_organs_response
    except ConnectionError:
        raise SpecialOrgansServerError('Failed to connect to the Special Organs server')



    