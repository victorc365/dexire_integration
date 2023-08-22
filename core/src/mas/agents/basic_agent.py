import logging

from spade.agent import Agent

from utils.string_builder import create_jid


class BasicAgent(Agent):
    def __init__(self, name: str):
        self.logger = logging.getLogger(f'[{name}]')
        self.id = create_jid(name)
        password = name
        super().__init__(self.id, password)