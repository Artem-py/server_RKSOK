import asyncio
import logging
import logging.config

from log_settings import logger_config
from request import get_request
from permission import get_permission
from response import form_response
from exceptions import ConnectionError, SpecialOrgansServerError, WrongRequestError


SERVER_ADDRESS = ('localhost', 8000)
ENCODING = 'UTF-8'

logging.config.dictConfig(logger_config)
logger = logging.getLogger('main')


async def handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Runs a full cycle of processing client's request:
        1. Receives client's request
        2. Parses the request 
        3. Turns to the Special Organs Response for permission to process the request
        4. Forms response and sends it back to client
    If something goes wrong during the cycle, handles possible exceptions and forms a response 
    according to the raised exception.
    
    """
    addr = writer.get_extra_info('peername')
    logger_name = 'main.ip_{}_port_{}'.format(*addr)
    logger = logging.getLogger(logger_name)
    logger.info('Connection accepted')

    client_response = ''
    logger.debug('Trying to receive a message from the client')
    try: 
        client_request = await get_request(reader)
        logger.debug('Request has been received:\r\n{!r}'.format(client_request.full_text[:150]))
        logger.debug('Connecting Special Organs Server')
        special_organs_response = await get_permission(client_request)
        logger.debug('Special Organs response is:\r\n{!r}'.format(special_organs_response))
        client_response = form_response(client_request, special_organs_response)
    
    except (ConnectionError, SpecialOrgansServerError) as e:
        logger.exception(e)
    
    except WrongRequestError as e:
        logger.exception(e)
        client_response = 'НИПОНЯЛ РКСОК/1.0\r\n\r\n'
    
    finally:
        if client_response:
            logger.debug('Sending response to the client, response is:\r\n{!r}'.format(client_response))
            writer.write(client_response.encode(ENCODING))
            await writer.drain()
        
        logger.info('Closing the connection')
        writer.close()
        await writer.wait_closed()
        return


async def main():
    """Starts server to work continuously in an asynchronous mode
    
    """
    server = await asyncio.start_server(handle_connection, *SERVER_ADDRESS)
    logger.debug('Starting up on {} port {}'.format(*SERVER_ADDRESS))

    async with server:
        await server.serve_forever()


asyncio.run(main())
