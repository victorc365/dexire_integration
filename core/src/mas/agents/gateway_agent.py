from mas.agents.basic_agent import BasicAgent
from spade.behaviour import CyclicBehaviour


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

    async def setup(self) -> None:
        await super().setup()
        self.add_behaviour(ListenerBehaviour())
        self.logger.debug('Setup and ready!')
