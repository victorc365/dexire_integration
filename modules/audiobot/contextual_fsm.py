import asyncio

from spade.message import Message

from mas.agents.personal_agent.behaviours.contextual_fsm import AbstractContextualFSMBehaviour
from spade.behaviour import State


class AudioState(State):

    def __init__(self) -> None:
        super().__init__()
        self.name = 'audioState'
        self.next_state = "audioState"

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
        audio_state = AudioState()
        self.add_state(name=audio_state.name,
                       state=audio_state,
                       initial=True)
        self.add_transition(audio_state.name, audio_state.next_state)

    async def on_start(self):
        await super().on_start()
