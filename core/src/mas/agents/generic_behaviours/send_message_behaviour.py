from spade.behaviour import OneShotBehaviour
from spade.message import Message

from mas.enums.message import MessageThread, MessageMetadata, MessageDirection, MessageTarget, MessageContext


class SendHemerappOutgoingMessageBehaviour(OneShotBehaviour):
    def __init__(self, to, sender, body, performative, metadata: dict) -> None:
        super().__init__()
        metadata.update({
            MessageMetadata.PERFORMATIVE.value: performative,
            MessageMetadata.TARGET.value: MessageTarget.HEMERAPP.value,
            MessageMetadata.DIRECTION.value: MessageDirection.OUTGOING.value
        })
        self.message = Message(
            to=str(to),
            sender=sender,
            body=body,
            thread=MessageThread.USER_THREAD.value,
            metadata=metadata
        )

    async def run(self) -> None:
        is_persisted_message = not self.message.get_metadata(
            MessageMetadata.CONTEXT.value) == MessageContext.HISTORY.value
        if is_persisted_message:
            self.agent.persistence_service.save_message_to_history(self.message)
        await self.send(self.message)


class SendHemerappIncomingMessageBehaviour(OneShotBehaviour):
    def __init__(self, to, sender, body, performative) -> None:
        super().__init__()
        self.message = Message(
            to=to,
            sender=sender,
            body=body,
            thread=MessageThread.USER_THREAD.value,
            metadata={
                MessageMetadata.PERFORMATIVE.value: performative,
                MessageMetadata.TARGET.value: MessageTarget.HEMERAPP.value,
                MessageMetadata.DIRECTION.value: MessageDirection.INCOMING.value
            }
        )

    async def run(self) -> None:
        await self.send(self.message)


class SendInternalMessageBehaviour(OneShotBehaviour):
    """ Behaviour responsible to send an internal message.

    Message sent by this behaviour are pre-configured to be sent on the internal thread.

    """

    def __init__(self, to, sender, body, performative, message_type) -> None:
        super().__init__()
        self.message = Message(
            to=to,
            sender=sender,
            body=body,
            thread=MessageThread.INTERNAL_THREAD.value,
            metadata={
                MessageMetadata.PERFORMATIVE.value: performative,
                MessageMetadata.TYPE.value: message_type
            }
        )

    async def run(self) -> None:
        await self.send(self.message)


class SendMessageBehaviour(OneShotBehaviour):
    """ Behaviour responsible to send a message.

    This behaviour sends a generic message. It does not set any configuration on it.

    """

    def __init__(self, to, sender, body, thread, metadata) -> None:
        super().__init__()
        self.message = Message(
            to=to,
            sender=sender,
            body=body,
            thread=thread,
            metadata=metadata
        )

    async def run(self) -> None:
        self.agent.logger.debug(f'Sending message: {self.message}')
        await self.send(self.message)
