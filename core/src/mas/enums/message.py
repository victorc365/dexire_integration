from enum import Enum


class MessageBodyFormat(Enum):
    IMAGE_TEXT = 'image_text'
    IMAGE = 'image'
    GIF = 'gif'
    TEXT = 'text'
    TEXT_TO_SPEECH = 'text_to_speech'


class MessageMetadata(Enum):
    """Enumeration of metadata that can be attached to a Message.

    Each incoming/outgoing message comes with a set of metadata that helps erebots to process them effectively.
    """
    ANSWER_TYPE = 'answer_type'
    ANSWERS = 'answers'
    BODY_FORMAT = 'body_format'
    CONTEXT = 'context'
    DIRECTION = 'direction'
    TARGET = 'target'
    PERFORMATIVE = 'performative'
    TYPE = 'type'


class MessageContext(Enum):
    """Enumeration of possible values for the metadata "context" of a Message.

    The context of a message is used to route the message to the correct handler. Each Personal agent has several
    finite state machines. When a message arrives in the MessageRouter of an agent, it is re-routed according to its
    context.
    """
    HISTORY = 'history'
    WELCOMING = 'welcoming'
    PROFILING = 'profiling'
    CONTEXTUAL = 'contextual'
    PERSUASION = 'persuasion'
    KEYBOARD = 'keyboard'


class MessageDirection(Enum):
    """ Enumeration of possible values for the metadata "direction" of a Message.

    The direction of a message indicates if the message is going through the gate way agent from the client to
    erebots or from erebots to the client.

    """
    INCOMING = 'incoming'
    OUTGOING = 'outgoing'


class MessagePerformative(Enum):
    """ Enumeration of FIPA performatives used in Erebots

    For more information, please have a look at http://www.fipa.org/specs/fipa00037/SC00037J.html
    """
    AGREE = 'agree'
    INFORM = 'inform'
    REFUSE = 'refuse'
    REQUEST = 'request'


class MessageTarget(Enum):
    """ Enumeration of possible values for the metadata "target" of a Message

    The target of a message is the system running the client communicating with erebots.
    It is used to indicate to the gateway agent from/to which format it has to decode an incoming/ouotgoing message.
    At the moment only hemerapp is supported but in the future, we may have client such as discord or telegram bots.

    """
    HEMERAPP = 'hemerapp'


class MessageType(Enum):
    """ Enumeration of possible values for the metadata "type" of a Message.

    The type of a message is used by the agents to distinguish the incoming message and be able to process them
    accordingly.

    """
    FREE_SLOTS = 'free_slots'
    AVAILABLE_GATEWAYS = 'available_gateways'
    OPENED_WEBSOCKET = 'opened_websocket'


class MessageThread(Enum):
    """ Enumeration of the available thread for the messages.

    The thread of the message is used to help the routing of messages inside the platform. When adding a behaviour
    to an agent, you can provide a template containing the specific thread to which the behaviour should listen to.

    """
    USER_THREAD = 'user-thread'
    INTERNAL_THREAD = 'internal-thread'
