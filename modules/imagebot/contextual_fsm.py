import asyncio

from spade.message import Message

from mas.agents.personal_agent.behaviours.contextual_fsm import AbstractContextualFSMBehaviour
from spade.behaviour import State
import json


class ReplyState(State):

    def __init__(self) -> None:
        super().__init__()
        self.name = "replyState"
        self.next_state = "replyState"

    async def run(self) -> None:
        while self.mailbox_size() == 0:
            await asyncio.sleep(1)
        message = await self.receive()
        reply = Message()
        reply.thread = message.thread
        reply.to = str(message.sender)
        reply.sender = str(message.to)
        reply.metadata = {'performative': 'inform', 'direction': 'outgoing', 'target': 'hemerapp',
                          'context': 'contextual', 'body_format': 'image'}
        reply.body = json.dumps({
            'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Hamburger_%28black_bg%29.jpg/250px-Hamburger_%28black_bg%29.jpg',
            'description': 'Super Healthy Burger'
        })
        self.agent.persistence_service.save_message_to_history(reply)

        await self.send(reply)


class ContextualFSM(AbstractContextualFSMBehaviour):
    def __init__(self):
        super().__init__()

    def setup(self):
        super().setup()
        reply_state = ReplyState()
        self.add_state(name=reply_state.name,
                       state=reply_state,
                       initial=True)
        self.add_transition(reply_state.name, reply_state.next_state)

    async def on_start(self):
        await super().on_start()
