from spade.behaviour import OneShotBehaviour

from mas.agents.gateway_agent.behaviours.forward_message_behaviour import ForwardMessageBehaviour


class FormatMessageBehaviour(OneShotBehaviour):
    """ One shot behaviour responsible to format message correctly.

    The FormatMessageBehaviour is called each time a message is coming from / is going through a websocket.
    Messages must contain the metadata "target" and "direction" to be processed correctly.
    Please see the enums MessageTarget and MessageDirection for more information about those metadata.

    Once, the message is formatted, the ForwardMessageBehaviour is automatically called.
    """

    def __init__(self) -> None:
        super().__init__()

    async def run(self):
        self.agent.add_behaviour(ForwardMessageBehaviour())
