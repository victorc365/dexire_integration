import json
from spade.behaviour import CyclicBehaviour

from mas.agents.generic_behaviours.send_message_behaviour import SendInternalMessageBehaviour
from mas.enums.message import MessagePerformative, MessageMetadata, MessageType


class InternalListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        message = await self.receive(timeout=1)
        if message is None:
            return

        message_type = message.get_metadata(MessageMetadata.TYPE.value)
        match message_type:
            case MessageType.AVAILABLE_GATEWAYS.value:
                performative = message.metadata[MessageMetadata.PERFORMATIVE.value]
                if performative == MessagePerformative.REQUEST.value:
                    self.agent.add_behaviour(SendInternalMessageBehaviour(
                        to=str(message.sender),
                        sender=str(message.to),
                        body=json.dumps(self.agent.services['gateway']),
                        performative=MessagePerformative.AGREE.value,
                        message_type=MessageType.AVAILABLE_GATEWAYS.value
                    ))
