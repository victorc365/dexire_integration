from spade.behaviour import FSMBehaviour, State

from enums.status import Status
from mas.enums.message import MessageThread
from services.chat_service import ChatService
from spade.message import Message
import json


class DynamicState(State):
    def __init__(self, config: dict) -> None:
        super().__init__()
        self.text = config['text']
        self.transition = config['transition'] if 'transition' in config.keys() else None

    async def run(self) -> None:
        gateway = ChatService().get_gateway(self.agent.id)
        message = Message()
        message.to = gateway
        message.sender = self.agent.id
        message.metadata = {'performative': 'inform', 'direction': 'outgoing', 'target': 'hemerapp'}
        message.body = json.dumps({"text:": "parfait michel"})
        message.thread = MessageThread.USER_THREAD.value
        await self.send(message)
        while True:
            message = await self.receive(timeout=1)
            if message is None:
                continue

            if self.transition is not None:
                self.next_state = self.transition
                break


class DynamicFSMBehaviour(FSMBehaviour):
    def __init__(self):
        super().__init__()
        self.config = None

    async def on_start(self) -> None:
        pass

    async def on_end(self) -> None:
        pass

    def setup(self):
        super().setup()
        states = self.config.states
        for i, state in enumerate(states):
            self.add_state(name=list(state.keys())[0],
                           state=DynamicState(state[list(state.keys())[0]]),
                           initial=(i == 0))
            if 'transition' in state[list(state.keys())[0]].keys():
                self.add_transition(list(state.keys())[0], state[list(state.keys())[0]]["transition"])
