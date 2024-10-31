import asyncio

from spade.behaviour import FSMBehaviour, State

from mas.agents.generic_behaviours.send_message_behaviour import SendHemerappOutgoingMessageBehaviour
from mas.enums.message import MessageMetadata, MessagePerformative, MessageContext, MessageBodyFormat
from services.chat_service import ChatService
import json


# TODO - Make it more generic using template methods and more configuration from yml file
class DynamicState(State):
    def __init__(self, config: dict, invalid_answer_message: str) -> None:
        super().__init__()
        self.text = config['text']
        self.answers = config['answers'] if 'answers' in config.keys() else None
        self.answer_type = config['answer_type'] if 'answer_type' in config.keys() else None
        self.transition = config['transition'] if 'transition' in config.keys() else None
        self.invalid_answer_message = invalid_answer_message
        self.field = config['field'] if 'field' in config.keys() else None

    def _is_valid_answer(self, answer) -> bool:
        is_valid = answer is not None
        match self.answer_type:
            case 'integer':
                try:
                    int(answer)
                except ValueError:
                    is_valid = False
            case 'options':
                is_valid = answer in self.answers
        return is_valid

    async def _send_message_and_wait_answer(self):
        """ This method is sending a message to the frontend and wait for the answer.

        As long as the provided answer is not valid, another message is sent to the frontend to ask for a correct answer.
        Once the answer is correct, it is returned.
        """
        gateway = ChatService().get_gateway(self.agent.id)
        metadata = {
            MessageMetadata.CONTEXT.value: MessageContext.PROFILING.value,
            MessageMetadata.ANSWER_TYPE.value: self.answer_type,
            MessageMetadata.BODY_FORMAT.value: MessageBodyFormat.TEXT.value
        }
        if self.answers is not None:
            buttons = []
            for answer in self.answers:
                buttons.append({'label': answer.replace('_', ' ').title(), 'action': answer})
            print(f"Buttons: {buttons}")
            metadata[MessageMetadata.ANSWERS.value] = json.dumps({"items": buttons})

        send_message = self.text
        answer = None
        is_valid_answer_provided = False
        mail_box = 0

        while not is_valid_answer_provided:
            self.agent.add_behaviour(SendHemerappOutgoingMessageBehaviour(
                to=gateway,
                sender=self.agent.id,
                body=send_message,
                performative=MessagePerformative.INFORM.value,
                metadata=metadata
            ))

            while self.mailbox_size() == mail_box:
                await asyncio.sleep(1)
            mail_box += 1

            message = await self.receive()
            if message is not None:
                answer = message.body
                is_valid_answer_provided = self._is_valid_answer(answer)
            send_message = f'Oups...{self.invalid_answer_message}'
        return answer

    async def run(self) -> None:
        answer = await self._send_message_and_wait_answer()
        if self.field:
            self.agent.profile[self.field] = answer

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
        invalid_answer_message = self.config.invalid_answer_message
        for i, state in enumerate(states):
            self.add_state(name=list(state.keys())[0],
                           state=DynamicState(state[list(state.keys())[0]], invalid_answer_message),
                           initial=(i == 0))
            if 'transition' in state[list(state.keys())[0]].keys():
                self.add_transition(list(state.keys())[0], state[list(state.keys())[0]]['transition'])
