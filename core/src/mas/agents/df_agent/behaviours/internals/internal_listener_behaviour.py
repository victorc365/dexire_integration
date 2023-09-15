import json

from aioxmpp import JID
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from mas.enums.message import MessagePerformative, MessageMetadata, MessageThread


class AvailableGatewayResponseMessage(Message):
    def __init__(self, to: JID, sender: JID, body: list[str]) -> None:
        super().__init__(
            to=str(to),
            sender=str(sender),
            body=json.dumps(body),
            thread=MessageThread.INTERNAL_THREAD.value,
            metadata={MessageMetadata.PERFORMATIVE.value: MessagePerformative.AGREE.value}
        )


class InternalListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        message = await self.receive(timeout=1)
        if message is None:
            return

        if message.metadata[MessageMetadata.PERFORMATIVE.value] == MessagePerformative.REQUEST.value:
            reply = AvailableGatewayResponseMessage(to=message.sender, sender=message.to,
                                                    body=self.agent.services['gateway'])
            await self.send(reply)
