from spade.behaviour import OneShotBehaviour

from mas.enums.message import MessageMetadata, MessageDirection


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
        bot_username = ''
        match direction:
            case MessageDirection.INCOMING.value:
                await self.send(self.message)
            case MessageDirection.OUTGOING.value:
                websocket = self.agent.clients[bot_username]
                await websocket.send(self.message)
