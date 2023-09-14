from aioxmpp import JID
from spade.message import Message
from starlette.websockets import WebSocketDisconnect

from mas.agents.gateway_agent.behaviours.format_message_behaviour import FormatMessageBehaviour
from services.bot_service import BotService
from mas.agents.basic_agent import BasicAgent, AgentType
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from mas.core_engine import CoreEngine
from mas.enums.message import MessageType, MessagePerformative, MessageMetadata, MessageTarget, MessageDirection
from enums.environment import Environment
import os


class FreeSlotGatewayResponseMessage(Message):
    def __init__(self, sender: JID, to: JID, performative: str) -> None:
        super().__init__(
            to=str(to),
            sender=str(sender),
            body=MessageType.FREE_SLOTS.value,
            metadata={MessageMetadata.PERFORMATIVE.value: performative}
        )


class ListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        message = await self.receive(timeout=1)
        if message is None:
            return

        if message.metadata[MessageMetadata.PERFORMATIVE.value] == MessagePerformative.REQUEST.value:
            if message.body == MessageType.FREE_SLOTS.value:
                current_clients_number = len(self.agent.clients.keys())
                max_clients_number = int(os.environ.get(Environment.MAXIMUM_CLIENTS_PER_GATEWAY.value))
                performative = MessagePerformative.REFUSE.value

                if current_clients_number < max_clients_number:
                    self.agent.clients[str(message.sender).split("@")[0]] = None
                    performative = MessagePerformative.AGREE.value

                reply = FreeSlotGatewayResponseMessage(to=message.sender, sender=message.to,
                                                       performative=performative)
                await self.send(reply)
        elif message.metadata[MessageMetadata.PERFORMATIVE.value] == MessagePerformative.INFORM.value:
            self.agent.add_behaviour(FormatMessageBehaviour(message))


class SetupBehaviour(OneShotBehaviour):
    def on_subscribe(self, jid):
        subscriber = jid.split("@")[0]
        self.agent.logger.debug(f'Agent {subscriber} asked for subscription.')
        bot_name = subscriber.split('_')[0]
        if bot_name in BotService().get_bots():
            number_clients = len(self.agent.clients.keys())
            maximum_clients = int(os.environ.get(Environment.MAXIMUM_CLIENTS_PER_GATEWAY.value))
            if number_clients >= maximum_clients:
                return
            self.agent.clients[subscriber] = None
            self.presence.subscribe(jid)
        self.agent.logger.info(f'Subscription from  {subscriber} approved.')
        self.presence.approve(jid)

    async def run(self):
        self.presence.on_subscribe = self.on_subscribe


class GatewayAgent(BasicAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.role = AgentType.GATEWAY_AGENT.value
        self.authorized_subscriptions.append(AgentType.PERSONAL_AGENT.value)
        self.clients = {}

    async def setup(self) -> None:
        await super().setup()
        self.add_behaviour(SetupBehaviour())
        self.add_behaviour(ListenerBehaviour())
        CoreEngine().df_agent.register(self)
        self.logger.debug('Setup and ready!')

    async def register_websocket(self, bot_user_name, websocket):
        if bot_user_name.lower() in self.clients.keys():
            self.clients[bot_user_name] = websocket
            await self.listen_on_websocket(bot_user_name, websocket)
        else:
            self.logger.error(f'Ignored websocket connection from {bot_user_name} because it was unexpected.')

    async def listen_on_websocket(self, bot_user_name, websocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                self.add_behaviour(
                    FormatMessageBehaviour(data, MessageDirection.INCOMING.value, MessageTarget.HEMERAPP.value))
        except WebSocketDisconnect:
            self.clients[bot_user_name] = None