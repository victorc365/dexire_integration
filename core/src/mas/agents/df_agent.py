from mas.agents.basic_agent import BasicAgent

from spade.behaviour import CyclicBehaviour
from mas.agents.basic_agent import AgentType


class ListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        message = await self.receive(timeout=1)
        if message is None:
            return


class DFAgent(BasicAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.add_behaviour(ListenerBehaviour())
        self.logger.debug('Setup and ready!')
