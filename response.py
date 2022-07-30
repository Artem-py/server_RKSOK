"""Contains functions to form responses

"""
import json

from permission import Permission
from request import Request


class ResponseTemplates:
    POSITIVE = 'НОРМАЛДЫКС РКСОК/1.0'
    NEGATIVE = 'НИЛЬЗЯ РКСОК/1.0'
    NO_SUCH_NAME = 'НИНАШОЛ РКСОК/1.0'
    DID_NOT_UNDERSTAND = 'НИПОНЯЛ РКСОК/1.0'


def form_response(request: Request, permission: Permission) -> str:
    if permission.permit == 'МОЖНА':
        response = get_data_from_phonebook(request)
    elif permission == 'НИЛЬЗЯ':
        response = ResponseTemplates.NEGATIVE + '\r\n' + permission.comment
    else:
        response = ResponseTemplates.DID_NOT_UNDERSTAND

    return response + '\r\n\r\n'


def get_data_from_phonebook(request: Request) -> str:
    """Works with PhoneBook database file based on the method variable value
    
    """
    with open('phonebook_DB.json', 'r') as f:
        phonebook_DB = json.load(f)

    if request.method == 'ЗОПИШИ':
        phonebook_DB[request.name] = request.contact_info
        response = ResponseTemplates.POSITIVE 
    elif request.method == 'ОТДОВАЙ':
        if request.name in phonebook_DB:
            response = ResponseTemplates.POSITIVE + '\r\n' + phonebook_DB[request.name]
        else:
            response = ResponseTemplates.NO_SUCH_NAME 
    elif request.method == 'УДОЛИ':
        if request.name in phonebook_DB:
            response = ResponseTemplates.POSITIVE
            del phonebook_DB[request.name]
        else:
             ResponseTemplates.NO_SUCH_NAME

    with open('phonebook_DB.json', 'w') as f:    
        json.dump(phonebook_DB, f)
    
    return response
