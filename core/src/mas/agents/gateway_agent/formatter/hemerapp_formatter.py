from mas.agents.gateway_agent.formatter.abstract_formatter import AbstractFormatter
import json
from spade.message import Message
from mas.enums.message import MessagePerformative, MessageDirection, MessageMetadata, MessageTarget, MessageThread
from utils.string_builder import create_jid


class HemerappIncomingMessage(Message):
    def __init__(self, sender: str = None, to: str = None, performative: str = None, body: str = None,
                 direction: str = None, context: str = None) -> None:
        super().__init__(
            to=to,
            sender=sender,
            body=str(body),
            thread=MessageThread.USER_THREAD.value,
            metadata={
                MessageMetadata.PERFORMATIVE.value: performative,
                MessageMetadata.DIRECTION.value: direction,
                MessageMetadata.TARGET.value: MessageTarget.HEMERAPP.value,
                MessageMetadata.CONTEXT.value: context
            }
        )


class HemerappOutgoingMessage:
    def __init__(self, sender: str, to: str, body: str, metadata: dict) -> None:
        self.to = to
        self.sender = sender
        self.body = body
        self.metadata = metadata


class HemerappFormatter(AbstractFormatter):
    def format_incoming_message(self, message):
        message_json = json.loads(message)
        return HemerappIncomingMessage(
            to=create_jid(message_json['to']),
            performative=MessagePerformative.INFORM.value,
            body=str(message_json['body']),
            direction=MessageDirection.INCOMING.value,
            context=message_json['metadata']['context']
        )

    def format_outgoing_message(self, message):
        to = message.sender.localpart.split('@')[0].split('_')[1]
        sender = message.sender.localpart
        return HemerappOutgoingMessage(
            to=to,
            sender=sender,
            body=str(message.body),
            metadata=message.metadata
        )
