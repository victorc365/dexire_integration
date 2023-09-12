from spade.behaviour import OneShotBehaviour

from mas.agents.gateway_agent.behaviours.forward_message_behaviour import ForwardMessageBehaviour
from mas.agents.gateway_agent.formatter.hemerapp_formatter import HemerappFormatter
from mas.enums.message import MessageMetadata, MessageTarget, MessageDirection


class FormatMessageBehaviour(OneShotBehaviour):
    """ One shot behaviour responsible to format message correctly.

    The FormatMessageBehaviour is called each time a message is coming from / is going through a websocket.
    Messages must contain the metadata "target" and "direction" to be processed correctly.
    Please see the enums MessageTarget and MessageDirection for more information about those metadata.

    Once, the message is formatted, the ForwardMessageBehaviour is automatically called.
    """

    def __init__(self, message, direction: MessageDirection = None, target: MessageTarget = None) -> None:
        super().__init__()
        self.message = message
        self.direction = message.get_metadata(MessageMetadata.DIRECTION.value) if direction is None else direction
        self.target = message.get_metadata(MessageMetadata.TARGET.value) if target is None else target

    async def run(self):
        formatted_message = None

        match self.target:
            case MessageTarget.HEMERAPP.value:
                formatter = HemerappFormatter()

        match self.direction:
            case MessageDirection.INCOMING.value:
                formatted_message = formatter.format_incoming_message(self.message)
            case MessageDirection.OUTGOING.value:
                formatted_message = formatter.format_outgoing_message(self.message)
        self.agent.add_behaviour(ForwardMessageBehaviour(formatted_message))
