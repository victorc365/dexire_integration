from enum import Enum


class Performative(Enum):
    """ Enumeration of FIPA performatives used in Erebots

    For more information, please have a look at http://www.fipa.org/specs/fipa00037/SC00037J.html
    """
    AGREE = 'agree'
    PERFORMATIVE = 'performative'
    REFUSE = 'refuse'
    REQUEST = 'request'
