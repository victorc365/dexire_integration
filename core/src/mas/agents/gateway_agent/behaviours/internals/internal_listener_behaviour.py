from aioxmpp import JID
from spade.message import Message
from spade.behaviour import CyclicBehaviour
from mas.enums.message import MessageType, MessagePerformative, MessageMetadata, MessageThread
from enums.environment import Environment
import os


class FreeSlotGatewayResponseMessage(Message):
    def __init__(self, sender: JID, to: JID, performative: str) -> None:
        super().__init__(
            to=str(to),
            sender=str(sender),
            body=MessageType.FREE_SLOTS.value,
            thread=MessageThread.INTERNAL_THREAD.value,
            metadata={
                MessageMetadata.PERFORMATIVE.value: performative,
                MessageMetadata.TYPE.value: MessageType.FREE_SLOTS.value
            }
        )


class InternalListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        message = await self.receive(timeout=1)
        if message is None:
            return

        message_type = message.get_metadata(MessageMetadata.TYPE.value)
        match message_type:
            case MessageType.FREE_SLOTS.value:
                performative = message.metadata[MessageMetadata.PERFORMATIVE.value]
                if performative == MessagePerformative.REQUEST.value:
                    current_clients_number = len(self.agent.clients.keys())
                    max_clients_number = int(os.environ.get(Environment.MAXIMUM_CLIENTS_PER_GATEWAY.value))
                    performative = MessagePerformative.REFUSE.value

                    if current_clients_number < max_clients_number:
                        self.agent.clients[str(message.sender).split("@")[0]] = None
                        performative = MessagePerformative.AGREE.value

                    reply = FreeSlotGatewayResponseMessage(to=message.sender, sender=message.to,
                                                           performative=performative)
                    await self.send(reply)
