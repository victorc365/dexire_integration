import logging

import spade
from enums.status import Status


class CoreEngine():
    def __init__(self):
        self._status = Status.TURNED_OFF.value
        self.logger = logging.getLogger('[CoreEngine] ->')
        self.agents = []

    def start(self) -> None:
        spade.run(self._start())

    def add_agent(self, agent):
        self.agents.append(agent)

    def _start(self) -> None:
        for agent in self.agents:
            agent.start()
        self._status = Status.RUNNING.value
