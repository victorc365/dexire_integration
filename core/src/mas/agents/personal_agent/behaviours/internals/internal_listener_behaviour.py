import json

from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message

from enums.status import Status
from mas.agents.personal_agent.behaviours.internals.register_to_gateway_behaviour import FreeSlotGatewayRequestMessage
from mas.agents.personal_agent.behaviours.profiling_fsm import ProfilingFSMBehaviour
from mas.enums.message import MessagePerformative, MessageType, MessageMetadata
from services.bot_service import BotService
from services.chat_service import ChatService


class EchoBehaviour(OneShotBehaviour):
    def __init__(self, message) -> None:
        super().__init__()
        self.message = message

    async def run(self) -> None:
        # TODO - remove this dummy behaviour when FSM is implemented
        message = Message()
        message.to = str(self.message.sender)
        message.sender = str(self.message.to)
        message.metadata = {'performative': 'inform', 'direction': 'outgoing', 'target': 'hemerapp'}
        message.body = self.message.body
        await self.send(message)


class InternalListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        message = await self.receive(timeout=1)
        print(message)
        if message is None:
            return
        if message.body == MessageType.FREE_SLOTS.value:
            if message.metadata[MessageMetadata.PERFORMATIVE.value] == MessagePerformative.AGREE.value:
                ChatService().register_gateway(str(message.sender), self.agent.id)
                self.agent.status = Status.RUNNING.value
                # TODO - find a way to start profiling with other behaviour even if it depends on the gateway registration
                profiling_configuration = BotService().get_bot_profiling(self.agent.id.split('_')[0])
                self.agent.add_behaviour(ProfilingFSMBehaviour(profiling_configuration))
            elif message.metadata[MessageMetadata.PERFORMATIVE.value] == MessagePerformative.REFUSE.value:
                message = FreeSlotGatewayRequestMessage(self.agent.id, self.agent.subscribed_gateways.pop())
                await self.send(message)

        elif message.metadata[MessageMetadata.PERFORMATIVE.value] == MessagePerformative.AGREE.value:
            gateways = json.loads(message.body)
            self.agent.last_gateway = gateways[-1]
            for gateway in gateways:
                if any(gateway == str(contact) for contact in self.presence.get_contacts()):
                    self.agent.subscribed_gateways.append(gateway)
            if len(self.agent.subscribed_gateways) > 0:
                message = FreeSlotGatewayRequestMessage(self.agent.id, self.agent.subscribed_gateways.pop())
                await self.send(message)
            else:
                # Use the most recent gateway as it should have available space
                self.presence.subscribe(self.agent.last_gateway)
        elif message.metadata[MessageMetadata.PERFORMATIVE.value] == MessagePerformative.INFORM.value:
            # TODO - forward to correct FSM when personal agent FSM are implemented
            self.agent.add_behaviour(EchoBehaviour(message))
