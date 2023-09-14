from mas.agents.basic_agent import BasicAgent, AgentType
from mas.agents.personal_agent.behaviours.profiling_fsm import ProfilingFSMBehaviour
from mas.enums.message import MessageType, MessagePerformative, MessageMetadata
from mas.core_engine import CoreEngine
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
import json

from services.bot_service import BotService
from services.chat_service import ChatService
from enums.status import Status


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


class SetupBehaviour(OneShotBehaviour):
    def on_subscribe(self, jid):
        subscriber = jid.split("@")[0]
        self.agent.logger.debug(f'Agent {subscriber} asked for subscription.')

        if AgentType.GATEWAY_AGENT.value in subscriber:
            self.agent.logger.info(f'Subscription from  {subscriber} approved.')
            self.presence.approve(jid)
            ChatService().register_gateway(jid, self.agent.id)
            self.agent.status = Status.RUNNING.value

    async def run(self):
        self.presence.on_subscribe = self.on_subscribe


class FreeSlotGatewayRequestMessage(Message):
    def __init__(self, sender: str, to: str) -> None:
        super().__init__(
            to=to,
            sender=sender,
            body=MessageType.FREE_SLOTS.value,
            metadata={MessageMetadata.PERFORMATIVE.value: MessagePerformative.REQUEST.value}
        )


class AvailableGatewayRequestMessage(Message):
    def __init__(self, sender: str) -> None:
        super().__init__(
            to=CoreEngine().df_agent.id,
            sender=sender,
            body=MessageType.AVAILABLE_GATEWAYS.value,
            metadata={MessageMetadata.PERFORMATIVE.value: MessagePerformative.REQUEST.value}
        )


class ListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        message = await self.receive(timeout=1)
        if message is None:
            return
        if message.body == MessageType.FREE_SLOTS.value:
            if message.metadata[MessageMetadata.PERFORMATIVE.value] == MessagePerformative.AGREE.value:
                ChatService().register_gateway(str(message.sender), self.agent.id)
                self.agent.status = Status.RUNNING.value
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


class RegisterToGatewayBehaviour(OneShotBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        # ask DF for available gateways
        message = AvailableGatewayRequestMessage(self.agent.id)
        await self.send(message)


class PersonalAgent(BasicAgent):
    def __init__(self, bot_user_name: str, password: str, token: str):
        super().__init__(bot_user_name)
        self.password = password
        self.token = token
        self.status = Status.TURNED_OFF.value
        self.last_gateway = None
        self.subscribed_gateways = []

    async def setup(self):
        self.logger.debug('Setup and ready!')
        await super().setup()
        self.add_behaviour(SetupBehaviour())
        self.add_behaviour(RegisterToGatewayBehaviour())
        self.add_behaviour(ListenerBehaviour())
        self.load_profiling_behaviour()

    def load_profiling_behaviour(self):
        profiling_configuration = BotService().get_bot_profiling(self.id.split('_')[0])

        if profiling_configuration is None:
            self.logger.debug('No profiling Configuration to load.')
            return

        if profiling_configuration.states is None:
            self.logger.error('Profiling configuration exists but no state has been defined. Skipping profiling FSM')
            return
        self.add_behaviour(ProfilingFSMBehaviour(profiling_configuration))
