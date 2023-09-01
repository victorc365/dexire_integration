from mas.agents.basic_agent import BasicAgent, AgentType
from mas.enums.performative import Performative
from mas.core_engine import CoreEngine
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
import json
from services.chat_service import ChatService
from enums.status import Status


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
            body="FREE_SLOTS",
            metadata={Performative.PERFORMATIVE.value: Performative.REQUEST.value}
        )


class AvailableGatewayRequestMessage(Message):
    def __init__(self, sender: str) -> None:
        super().__init__(
            to=CoreEngine().df_agent.id,
            sender=sender,
            body="AVAILABLE_GATEWAYS",
            metadata={Performative.PERFORMATIVE.value: Performative.REQUEST.value}
        )


class ListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        message = await self.receive(timeout=1)
        if message is None:
            return

        if message.body == 'FREE_SLOTS':
            if message.metadata[Performative.PERFORMATIVE.value] == Performative.AGREE.value:
                ChatService().register_gateway(str(message.sender), self.agent.id)
                self.agent.status = Status.RUNNING.value
            elif message.metadata[Performative.PERFORMATIVE.value] == Performative.REFUSE.value:
                message = FreeSlotGatewayRequestMessage(self.agent.id, self.agent.subscribed_gateways.pop())
                await self.send(message)

        elif message.metadata[Performative.PERFORMATIVE.value] == Performative.AGREE.value:
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
