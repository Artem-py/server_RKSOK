"""Customed Exceptions

"""
class DisconnectionError(Exception):
    """Raised when client gets disconnected
    """
    pass

class ConnectionError(Exception):
    """Raised when server has failed to receive a message from a client
    """
    pass

class  WrongRequestError(Exception):
    """Raised when request is sintactically incorrect"""
    pass

class SpecialOrgansServerError(Exception):
    """Raised when server has failed to receive message from the Special Organs Server
    """
    pass
