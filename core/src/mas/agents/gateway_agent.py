from mas.agents.basic_agent import BasicAgent, AgentType
from spade.behaviour import CyclicBehaviour
from mas.core_engine import CoreEngine


class ListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        message = await self.receive(timeout=1)
        if message is None:
            return


class GatewayAgent(BasicAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.role = AgentType.GATEWAY_AGENT.value

    async def setup(self) -> None:
        await super().setup()
        self.add_behaviour(ListenerBehaviour())
        CoreEngine().df_agent.register(self)
        self.logger.debug('Setup and ready!')
