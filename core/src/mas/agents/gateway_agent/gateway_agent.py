from starlette.websockets import WebSocketDisconnect

from mas.agents.gateway_agent.behaviours.external_listener_behaviour import ExternalListenerBehaviour
from mas.agents.gateway_agent.behaviours.format_message_behaviour import FormatMessageBehaviour
from mas.agents.basic_agent import BasicAgent, AgentType
from mas.agents.gateway_agent.behaviours.internals.internal_listener_behaviour import InternalListenerBehaviour
from mas.agents.gateway_agent.behaviours.internals.setup_behaviour import SetupBehaviour
from mas.agents.generic_behaviours.send_message_behaviour import SendInternalMessageBehaviour
from mas.core_engine import CoreEngine
from mas.enums.message import MessageTarget, MessageDirection, MessageType, MessagePerformative
from utils.communication_utils import get_internal_thread_template, get_user_thread_template
from utils.string_builder import create_jid


class GatewayAgent(BasicAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.role = AgentType.GATEWAY_AGENT.value
        self.authorized_subscriptions.append(AgentType.PERSONAL_AGENT.value)
        self.clients = {}

    async def setup(self) -> None:
        await super().setup()
        self.add_behaviour(SetupBehaviour())
        self.add_behaviour(InternalListenerBehaviour(), get_internal_thread_template())
        self.add_behaviour(ExternalListenerBehaviour(), get_user_thread_template())

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
        self.add_behaviour(SendInternalMessageBehaviour(
            to=create_jid(bot_user_name),
            sender=self.id,
            message_type=MessageType.OPENED_WEBSOCKET.value,
            performative=MessagePerformative.INFORM.value,
            body=None

        ))
        try:
            while True:
                data = await websocket.receive_text()
                self.add_behaviour(
                    FormatMessageBehaviour(data, MessageDirection.INCOMING.value, MessageTarget.HEMERAPP.value))
        except WebSocketDisconnect:
            self.clients[bot_user_name] = None
