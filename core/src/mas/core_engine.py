import logging

import spade
from mas.agents.gateway_agent import GatewayAgent


class CoreEngine():
    def __init__(self):
        self.logger = logging.getLogger('[CoreEngine] ->')
        self.agents = []
        self._setup()

    def _setup(self):
        gateway_agent = GatewayAgent('gateway_agent_1')
        self.agents.append(gateway_agent)

    def start(self) -> None:
        spade.run(self._start())

    async def _start(self) -> None:
        for agent in self.agents:
            await agent.start()
