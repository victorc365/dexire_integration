from spade.behaviour import CyclicBehaviour
from spade.behaviour import OneShotBehaviour

from mas.agents.basic_agent import BasicAgent
from mas.agents.personal_agent import PersonalAgent


class ListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        message = await self.receive(timeout=1)
        if message is None:
            return


class CreatePersonalAgentBehaviour(OneShotBehaviour):
    def __init__(self, bot_user_name: str, password: str, token: str) -> None:
        super().__init__()
        self.new_agent = PersonalAgent(bot_user_name, password, token)

    async def run(self) -> None:
        await self.new_agent.start(auto_register=True)


class GatewayAgent(BasicAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    async def setup(self) -> None:
        await super().setup()
        self.add_behaviour(ListenerBehaviour())
        self.logger.debug('Setup and ready!')

    async def create_agent(self, bot_user_name: str, password: str, token: str) -> None:
        behaviour = CreatePersonalAgentBehaviour(bot_user_name, password, token)
        self.add_behaviour(behaviour)