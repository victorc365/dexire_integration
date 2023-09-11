from spade.behaviour import OneShotBehaviour

from mas.enums.message import MessageMetadata, MessageDirection
import json
class ForwardMessageBehaviour(OneShotBehaviour):
    """ One shot behaviour responsible to forward message to correct destination.

        The ForwardMessageBehaviour is called each time a message is coming from / is going through a websocket.
        Messages must contain the metadata "target" and "direction" to be processed correctly.
        Please see the enums MessageTarget and MessageDirection for more information about those metadata.
        """

    def __init__(self, message) -> None:
        super().__init__()
        self.message = message

    async def run(self):
        direction = self.message.get_metadata(MessageMetadata.DIRECTION.value)
        match direction:
            case MessageDirection.INCOMING.value:
                await self.send(self.message)
            case MessageDirection.OUTGOING.value:

                # TODO - refactor for better code
                to = self.message.sender.localpart

                websocket = self.agent.clients[to]
                message = {
                    'to': self.message.sender.localpart.split('@')[0].split('_')[1],
                    'sender': self.message.sender.localpart,
                    'body': self.message.body,
                    'metadata': self.message.metadata
                }
                await websocket.send_text(json.dumps(message))
