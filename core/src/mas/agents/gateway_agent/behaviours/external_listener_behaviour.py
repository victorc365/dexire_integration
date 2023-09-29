from spade.behaviour import CyclicBehaviour

from mas.agents.gateway_agent.behaviours.format_message_behaviour import FormatMessageBehaviour
from mas.enums.message import MessageMetadata, MessagePerformative


class ExternalListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        message = await self.receive(timeout=1)
        if message is None:
            return
        if message.metadata[MessageMetadata.PERFORMATIVE.value] == MessagePerformative.INFORM.value:
            self.agent.add_behaviour(FormatMessageBehaviour(message))
