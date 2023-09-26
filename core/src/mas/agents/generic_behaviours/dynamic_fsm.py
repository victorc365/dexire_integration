import asyncio

from spade.behaviour import FSMBehaviour, State

from mas.enums.message import MessageThread, MessageMetadata, MessagePerformative, MessageDirection, MessageTarget, \
    MessageContext
from services.chat_service import ChatService
from spade.message import Message
import json

# TODO - Make it more generic using template methods and more configuration from yml file
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
        message.metadata = {
            MessageMetadata.PERFORMATIVE.value: MessagePerformative.INFORM.value,
            MessageMetadata.DIRECTION.value: MessageDirection.OUTGOING.value,
            MessageMetadata.TARGET.value: MessageTarget.HEMERAPP.value,
            MessageMetadata.CONTEXT.value: MessageContext.PROFILING.value}
        message.body = json.dumps({"text": f"{self.text}"})
        message.thread = MessageThread.USER_THREAD.value
        await self.send(message)

        while self.mailbox_size() == 0:
            await asyncio.sleep(1)

        message = await self.receive()

        # TODO - Save message in Pryv and process it if necessary
        #print(message)
        if self.transition is not None:
            self.next_state = self.transition
        else:
            self.kill()


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
