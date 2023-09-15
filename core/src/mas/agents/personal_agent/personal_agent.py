from spade.template import Template

from mas.agents.basic_agent import BasicAgent
from mas.agents.personal_agent.behaviours.internals.internal_listener_behaviour import InternalListenerBehaviour
from mas.agents.personal_agent.behaviours.internals.register_to_gateway_behaviour import RegisterToGatewayBehaviour
from mas.agents.personal_agent.behaviours.internals.setup_behaviour import SetupBehaviour
from enums.status import Status
from mas.agents.personal_agent.behaviours.messages_router import MessagesRouterBehaviour
from mas.enums.message import MessageThread


class PersonalAgent(BasicAgent):
    def __init__(self, bot_user_name: str, password: str, token: str):
        super().__init__(bot_user_name)
        self.password = password
        self.token = token
        self.status = Status.TURNED_OFF.value
        self.last_gateway = None
        self.subscribed_gateways = []

    async def setup(self):
        await super().setup()
        internal_communication_template = Template()
        internal_communication_template.thread = MessageThread.INTERNAL_THREAD.value

        user_communication_template = Template()
        user_communication_template.thread = MessageThread.USER_THREAD.value
        self.add_behaviour(SetupBehaviour())
        self.add_behaviour(RegisterToGatewayBehaviour())
        self.add_behaviour(InternalListenerBehaviour(), internal_communication_template)
        self.add_behaviour(MessagesRouterBehaviour(), user_communication_template)
        self.logger.debug('Setup and ready!')
