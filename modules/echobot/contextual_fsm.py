import asyncio

from spade.message import Message

from core.src.mas.agents.personal_agent.behaviours.contextual_fsm import AbstractContextualFSMBehaviour
from spade.behaviour import State

import json

class EchoState(State):
    def __init__(self) -> None:
        super().__init__()
        self.next_state = "echoState"
        self.count = 1

    async def run(self) -> None:
        while self.mailbox_size() == 0:
            await asyncio.sleep(1)
        message = await self.receive()

        metadata = {
          'performative': 'inform',
          'direction': 'outgoing',
          'target': 'hemerapp',
          'context': 'keyboard',
          'body_format': 'text'
        }

        print("MESSAGE: ")
        print(message.thread)      
        print(message.sender)
        print(message.to)
        reply = Message()
        reply.thread = message.thread
        reply.to = str(message.sender)
        reply.sender = str(message.to)
        reply.metadata = metadata         #{'performative': 'inform', 'direction': 'outgoing', 'target': 'hemerapp',
                                          # 'context': 'contextual', 'body_format': 'text'}
        reply.body = json.dumps({
          "items": [
            {
              "label": str(message.body),
              "action": "ECHO"
            },
          ]
        })

        print("Keyboard Message: ", reply)


#2024-01-30 14:02:26,698 [DEBUG] spade.Message: message matched <template to="None" from="None" thread="user-thread" metadata={}></template> == <message to="gateway_agent_1@localhost" from="nvcbot_berkbuzcu@localhost" thread="user-thread" metadata={'performative': 'inform', 'direction': 'outgoing', 'target': 'hemerapp', 'context': 'keyboard', 'body_format': 'text'}>
#{"items": [{"label": "none", "action": "none"}, {"label": NaN, "action": NaN}, {"label": "soy", "action": "soy"}, {"label": "nuts", "action": "nuts"}, {"label": "dairy", "action": "dairy"}, {"label": "eggs", "action": "eggs"}, {"label": "shellfish", "action": "shellfish"}, {"label": "Continue", "action": "CONTINUE"}]}
#</message>


        self.agent.persistence_service.save_message_to_history(reply)
        await self.send(reply)


class ContextualFSM(AbstractContextualFSMBehaviour):
    def __init__(self):
        super().__init__()

    def setup(self):
        super().setup()

        self.add_state(name="echoState",
                       state=EchoState(),
                       initial=True)
        self.add_transition("echoState", "echoState")

    async def on_start(self):
        await super().on_start()
