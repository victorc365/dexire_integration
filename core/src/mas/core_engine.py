import logging
from typing import List

import setup
import spade
from enums.status import Status
from fastapi import FastAPI
from spade.agent import Agent


class CoreEngine():
    def __init__(self):
        self._status = Status.TURNED_OFF.value
        self.logger = logging.getLogger('[CoreEngine]')
        self.agents: List[Agent] = []
        self.api: FastAPI

    def start(self) -> None:
        spade.run(self._start())

    def add_agent(self, agent: Agent) -> None:
        self.agents.append(agent)

    async def _start(self) -> None:
        for agent in self.agents:
            await agent.start()
        self._status = Status.RUNNING.value
        container = spade.container.Container()
        self.api = await setup.init_api(container.loop)
        await spade.wait_until_finished(self.agents)
