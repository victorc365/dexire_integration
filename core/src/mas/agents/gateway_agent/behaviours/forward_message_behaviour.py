from spade.behaviour import OneShotBehaviour


class ForwardMessageBehaviour(OneShotBehaviour):
    """ One shot behaviour responsible to forward message to correct destination.

        The ForwardMessageBehaviour is called each time a message is coming from / is going through a websocket.
        Messages must contain the metadata "target" and "direction" to be processed correctly.
        Please see the enums MessageTarget and MessageDirection for more information about those metadata.
        """
    def __init__(self) -> None:
        super().__init__()

    async def run(self):
        print("forwarding message")
