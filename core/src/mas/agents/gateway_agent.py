
from mas.agents.basic_agent import BasicAgent


class GatewayAgent(BasicAgent):
    def __init__(self, name: str):
        super().__init__(name)

    async def setup(self):
        self.logger.debug('Setup and ready!')
        return await super().setup()