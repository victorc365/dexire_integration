import asyncio

from mas.agents.basic_agent import BasicAgent
from spade.behaviour import CyclicBehaviour


class DummyAgent(BasicAgent):
    def __init__(self, name: str):
        super().__init__(name)

    async def setup(self):
        self.logger.info('starting...')
        behaviour = self.DummyBehaviour(self, self.logger)
        self.add_behaviour(behaviour)

    class DummyBehaviour(CyclicBehaviour):
        def __init__(self, agent, logger):
            super().__init__()
            self.counter = 0
            self.logger = logger
            self.agent = agent

        async def run(self):
            self.logger.debug('count : ' + str(self.counter))
            self.counter += 1
            if self.counter == 10:
                self.kill(exit_code=10)
                await self.agent.stop()
            await asyncio.sleep(1)
