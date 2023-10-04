import asyncio

from spade.behaviour import FSMBehaviour, State

from mas.agents.generic_behaviours.send_message_behaviour import SendHemerappOutgoingMessageBehaviour
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
        self.answers = config['answers'] if 'answers' in config.keys() else None
        self.answer_type = config['answer_type'] if 'answer_type' in config.keys() else None
        self.transition = config['transition'] if 'transition' in config.keys() else None

    async def run(self) -> None:
        gateway = ChatService().get_gateway(self.agent.id)
        metadata = {
            MessageMetadata.CONTEXT.value: MessageContext.PROFILING.value,
            MessageMetadata.ANSWER_TYPE.value: self.answer_type,
        }

        if self.answers is not None:
            metadata[MessageMetadata.ANSWERS.value] = self.answers

        behaviour = SendHemerappOutgoingMessageBehaviour(
            to=gateway,
            sender=self.agent.id,
            body=self.text,
            performative=MessagePerformative.INFORM.value,
            metadata=metadata
        )
        self.agent.add_behaviour(behaviour)

        while self.mailbox_size() == 0:
            await asyncio.sleep(1)

        message = await self.receive()

        # TODO - Save message in Pryv and process it if necessary
        # print(message)
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
                self.add_transition(list(state.keys())[0], state[list(state.keys())[0]]['transition'])
