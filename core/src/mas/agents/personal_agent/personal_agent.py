from spade.template import Template

from mas.agents.basic_agent import BasicAgent
from mas.agents.personal_agent.behaviours.internals.internal_listener_behaviour import InternalListenerBehaviour
from mas.agents.personal_agent.behaviours.internals.register_to_gateway_behaviour import RegisterToGatewayBehaviour
from mas.agents.personal_agent.behaviours.internals.setup_behaviour import SetupBehaviour
from enums.status import Status


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
        self.add_behaviour(InternalListenerBehaviour())
