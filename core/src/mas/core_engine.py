import asyncio
import logging
import sys

import spade

import setup
from enums.status import Status
from mas.agents.ams_agent.ams_agent import AMSAgent
from mas.agents.basic_agent import BasicAgent
from mas.agents.df_agent.df_agent import DFAgent
from utils.metaclasses.singleton import Singleton
from spade.container import Container


class CoreEngine(metaclass=Singleton):
    def __init__(self, run_api=True):
        self._status = Status.TURNED_OFF.value
        self.logger = logging.getLogger('[CoreEngine]')
        self.run_api = run_api
        self.ams_agent = AMSAgent('ams_agent')
        self.df_agent = DFAgent('df_agent')
        self.container = None

    def start(self) -> None:
        spade.run(self._start())

    async def _start(self) -> None:
        await self._create_default_agents()

        self._status = Status.RUNNING.value
        container = Container()
        self.container = container
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
            await spade.wait_until_finished(self.agents)
        await self.ams_agent.stop_agents()

    async def create_personal_agent(self, bot_user_name: str, token: str, descriptor):
        # TODO - Find a way to solve the circular dependency which does not imply to put import here
        from mas.agents.personal_agent.personal_agent import PersonalAgent
        await self._create_agent(PersonalAgent(bot_user_name, bot_user_name, token, descriptor))

    async def create_gateway_agent(self, name: str):
        # TODO - Find a way to solve the circular dependency which does not imply to put import here
        from mas.agents.gateway_agent.gateway_agent import GatewayAgent
        await self._create_agent(GatewayAgent(name))

    async def _create_default_agents(self):
        await self.ams_agent.start(auto_register=True)
        await self.ams_agent.create_agent(self.df_agent)
        await self.create_gateway_agent('gateway_agent_1')

    async def _create_agent(self, agent: BasicAgent):
        await self.ams_agent.create_agent(agent)
