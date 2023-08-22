import asyncio
import logging
import sys
from typing import List

import spade
from spade.container import Container

import setup
from enums.status import Status
from mas.agents.basic_agent import BasicAgent
from mas.agents.gateway_agent import GatewayAgent
from utils.metaclasses.singleton import Singleton


class CoreEngine(metaclass=Singleton):
    def __init__(self, run_api=True):
        self._status = Status.TURNED_OFF.value
        self.logger = logging.getLogger('[CoreEngine]')
        self.agents: List[BasicAgent] = []
        self.run_api = run_api
        self.master_gateway_agent: str = None

    def start(self) -> None:
        spade.run(self._start())

    def add_agent(self, agent: BasicAgent) -> None:
        if 'gateway_agent_1' in agent.id:
            self.master_gateway_agent = agent.id
        self.agents.append(agent)

    async def _start(self) -> None:
        for agent in self.agents:
            await agent.start(auto_register=True)
        self._status = Status.RUNNING.value
        container = spade.container.Container()
        if self.run_api:
            server = setup.init_api(container.loop)
            # KeyboardInterrupt is caught by uvicorn and spade never shutdown
            # We shutdown manually the app
            try:
                await server.serve()
            finally:
                loop = asyncio.get_event_loop()
                loop.call_soon_threadsafe(loop.stop)
                sys.exit(0)
        else:
            spade.wait_until_finished(self.agents)

    async def create_agent(self, bot_user_name: str, token: str):
        container: Container = Container()
        gateway_agent: GatewayAgent = container.get_agent(self.master_gateway_agent)
        await gateway_agent.create_agent(bot_user_name, bot_user_name, token)
