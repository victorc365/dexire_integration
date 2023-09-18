import importlib
from mas.agents.basic_agent import BasicAgent
from mas.agents.personal_agent.behaviours.internals.internal_listener_behaviour import InternalListenerBehaviour
from mas.agents.personal_agent.behaviours.internals.register_to_gateway_behaviour import RegisterToGatewayBehaviour
from mas.agents.personal_agent.behaviours.internals.setup_behaviour import SetupBehaviour
from enums.status import Status
from mas.agents.personal_agent.behaviours.messages_router import MessagesRouterBehaviour
from mas.enums.message import MessageContext
from utils.communication_utils import get_internal_thread_template, get_user_thread_template


class PersonalAgent(BasicAgent):
    def __init__(self, bot_user_name: str, password: str, token: str):
        super().__init__(bot_user_name)
        self.password = password
        self.token = token
        self.status = Status.TURNED_OFF.value
        self.last_gateway = None
        self.subscribed_gateways = []
        self.message_router = MessagesRouterBehaviour()
        self.module_name = bot_user_name.split('_')[0]
        self.contextual_module = getattr(importlib.import_module(f'modules.{self.module_name}.contextual_fsm'),
                                         'ContextualFSM')

    async def setup(self):
        await super().setup()
        self.add_behaviour(SetupBehaviour())
        self.add_behaviour(RegisterToGatewayBehaviour())
        self.add_behaviour(InternalListenerBehaviour(), get_internal_thread_template())
        self.add_behaviour(self.message_router, get_user_thread_template())
        self.add_contextual_behaviour(MessageContext.CONTEXTUAL.value, self.contextual_module())
        self.logger.debug('Setup and ready!')

    def add_contextual_behaviour(self, context: MessageContext, behaviour, template=None):
        self.add_behaviour(behaviour, template)
        self.message_router.set_address(context, behaviour)
