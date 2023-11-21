import asyncio

from spade.message import Message

from mas.agents.personal_agent.behaviours.contextual_fsm import AbstractContextualFSMBehaviour
from spade.behaviour import State


class AudioState(State):

    def __init__(self) -> None:
        super().__init__()
        self.next_state = "audiobot"

    async def run(self) -> None:
        while self.mailbox_size() == 0:
            await asyncio.sleep(1)
        message = await self.receive()
        reply = Message()
        reply.thread = message.thread
        reply.to = str(message.sender)
        reply.sender = str(message.to)
        reply.metadata = {'performative': 'inform', 'direction': 'outgoing', 'target': 'hemerapp',
                          'context': 'contextual', 'body_format': 'text_to_speech'}
        reply.body = message.body
        self.agent.persistence_service.save_message_to_history(reply)

        await self.send(reply)


class ContextualFSM(AbstractContextualFSMBehaviour):
    def __init__(self):
        super().__init__()

    def setup(self):
        super().setup()

        self.add_state(name="audioState",
                       state=AudioState(),
                       initial=True)
        self.add_transition("audioState", "audioState")

    async def on_start(self):
        await super().on_start()
