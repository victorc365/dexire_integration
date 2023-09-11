from abc import ABC, abstractmethod


class AbstractFormatter(ABC):
    """ Definition of required method for FormatMessageBehaviour.

    This class defines all methods that must be implemented in order to make the FormatMessageBehaviour work correctly
    with the target system.
    """

    @abstractmethod
    def format_incoming_message(self, message):
        pass

    @abstractmethod
    def format_outgoing_message(self, message):
        pass
