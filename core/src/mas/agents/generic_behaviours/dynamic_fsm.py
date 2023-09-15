from spade.behaviour import FSMBehaviour, State

from enums.status import Status
from services.chat_service import ChatService
from spade.message import Message


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
        message.body = {"text:":"parfait michel"}
        await self.send(message)
        while True:
            message = await self.receive(timeout=1)
            print(message)
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
        while self.agent.status != Status.RUNNING.value:
            print('waiting to be running')

    async def on_end(self) -> None:
        pass

    def setup(self):
        super().setup()
        states = self.config.states
        for i, state in enumerate(states):
            print(state)
            self.add_state(name=list(state.keys())[0],
                          state=DynamicState(state[list(state.keys())[0]]),
                          initial=(i == 0))
            if 'transition' in state[list(state.keys())[0]].keys():
                self.add_transition(list(state.keys())[0], state[list(state.keys())[0]]["transition"])


