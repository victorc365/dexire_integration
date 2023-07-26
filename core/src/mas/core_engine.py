import asyncio
import logging
import sys
from typing import List

import setup
import spade
from enums.status import Status
from spade.agent import Agent


class CoreEngine():
    def __init__(self, run_api=True):
        self._status = Status.TURNED_OFF.value
        self.logger = logging.getLogger('[CoreEngine]')
        self.agents: List[Agent] = []
        self.run_api = run_api

    def start(self) -> None:
        spade.run(self._start())

    def add_agent(self, agent: Agent) -> None:
        self.agents.append(agent)

    async def _start(self) -> None:
        for agent in self.agents:
            await agent.start()
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