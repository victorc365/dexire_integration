import importlib
from mas.agents.basic_agent import BasicAgent
from mas.agents.personal_agent.behaviours.internals.internal_listener_behaviour import InternalListenerBehaviour
from mas.agents.personal_agent.behaviours.internals.register_to_gateway_behaviour import RegisterToGatewayBehaviour
from mas.agents.personal_agent.behaviours.internals.setup_behaviour import SetupBehaviour
from enums.status import Status
from mas.agents.personal_agent.behaviours.messages_router import MessagesRouterBehaviour
from mas.enums.message import MessageContext
from services.bot_service import Bot
from services.persistence_service import PryvPersistenceService
from utils.communication_utils import get_internal_thread_template, get_user_thread_template, \
    get_contextual_fsm_template


class PersonalAgent(BasicAgent):
    def __init__(self, bot_user_name: str, password: str, token: str, descriptor: Bot):
        super().__init__(bot_user_name)
        self.password = password
        self.token = token
        self.status = Status.TURNED_OFF.value
        self.last_gateway = None
        self.subscribed_gateways = []
        self.message_router = MessagesRouterBehaviour()
        self.module_name, self.user = bot_user_name.split('_', 1)
        self.persistence_service = PryvPersistenceService(self.user, self.module_name, token)
        self.profile = {}
        if descriptor is not None and descriptor.is_update_required:
            self.persistence_service.deploy_model(descriptor.required_streams)
        try:
            self.contextual_module = getattr(importlib.import_module(f'modules.{self.module_name}.contextual_fsm'),
                                             'ContextualFSM')
        except ModuleNotFoundError:
            self.contextual_module = None

    async def setup(self):
        await super().setup()
        self.add_behaviour(SetupBehaviour())
        self.add_behaviour(RegisterToGatewayBehaviour())
        self.add_behaviour(InternalListenerBehaviour(), get_internal_thread_template())
        self.add_behaviour(self.message_router, get_user_thread_template())
        if self.contextual_module is not None:
            self.add_contextual_behaviour(MessageContext.CONTEXTUAL.value, self.contextual_module(),
                                          get_contextual_fsm_template())
        self.logger.debug('Setup and ready!')

    def add_contextual_behaviour(self, context: MessageContext, behaviour, template=None):
        self.add_behaviour(behaviour, template)
        self.message_router.set_address(context, behaviour)
