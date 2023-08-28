import asyncio
import logging
import sys

import spade

import setup
from enums.status import Status
from mas.agents.basic_agent import BasicAgent
from mas.agents.df_agent import DFAgent
from mas.agents.ams_agent import AMSAgent
from mas.agents.personal_agent import PersonalAgent
from utils.metaclasses.singleton import Singleton


class CoreEngine(metaclass=Singleton):
    def __init__(self, run_api=True):
        self._status = Status.TURNED_OFF.value
        self.logger = logging.getLogger('[CoreEngine]')
        self.run_api = run_api
        self.ams_agent = AMSAgent('ams_agent')
        self.df_agent = DFAgent('df_agent')

    def start(self) -> None:
        spade.run(self._start())

    async def _start(self) -> None:
        await self._create_default_agents()

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
            await spade.wait_until_finished(self.agents)

    async def create_personal_agent(self, bot_user_name: str, token: str):
        await self._create_agent(PersonalAgent(bot_user_name, bot_user_name, token))

    async def create_gateway_agent(self, name: str):
        # TODO - Find a way to solve the circular dependency which does not imply to put import here
        from mas.agents.gateway_agent import GatewayAgent
        await self._create_agent(GatewayAgent(name))

    async def _create_default_agents(self):
        await self.ams_agent.start(auto_register=True)
        await self.ams_agent.create_agent(self.df_agent)
        await self.create_gateway_agent('gateway_agent_1')

    async def _create_agent(self, agent: BasicAgent):
        await self.ams_agent.create_agent(agent)