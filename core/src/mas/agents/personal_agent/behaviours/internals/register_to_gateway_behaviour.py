from spade.behaviour import OneShotBehaviour
from spade.message import Message

from mas.core_engine import CoreEngine
from mas.enums.message import MessageType, MessageMetadata, MessagePerformative, MessageThread


class FreeSlotGatewayRequestMessage(Message):
    def __init__(self, sender: str, to: str) -> None:
        super().__init__(
            to=to,
            sender=sender,
            body=MessageType.FREE_SLOTS.value,
            thread=MessageThread.INTERNAL_THREAD.value,
            metadata={MessageMetadata.PERFORMATIVE.value: MessagePerformative.REQUEST.value}
        )


class AvailableGatewayRequestMessage(Message):
    def __init__(self, sender: str) -> None:
        super().__init__(
            to=CoreEngine().df_agent.id,
            sender=sender,
            body=MessageType.AVAILABLE_GATEWAYS.value,
            thread=MessageThread.INTERNAL_THREAD.value,
            metadata={MessageMetadata.PERFORMATIVE.value: MessagePerformative.REQUEST.value}
        )


class RegisterToGatewayBehaviour(OneShotBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        # ask DF for available gateways
        message = AvailableGatewayRequestMessage(self.agent.id)
        await self.send(message)
