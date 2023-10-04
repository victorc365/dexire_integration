import logging
from enum import Enum

from aioxmpp import PresenceState, PresenceShow
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from utils.string_builder import create_jid


class AgentType(Enum):
    PERSONAL_AGENT = 'personal'
    GATEWAY_AGENT = 'gateway'
    DF_AGENT = 'df'
    DUMMY_AGENT = 'dummy'
    AMS_AGENT = 'ams'


class BasicSetupBehaviour(OneShotBehaviour):
    def on_subscribe(self, jid):
        subscriber = jid.split("@")[0]
        self.agent.logger.debug(f'Agent {subscriber} asked for subscription.')
        if any(authorized in subscriber for authorized in self.agent.authorized_subscriptions):
            self.agent.logger.info(f'Subscription from  {subscriber} approved.')
            self.presence.approve(jid)
        else:
            self.agent.logger.warning(f'Agent {subscriber} is not authorized for subscription.')

    async def run(self):
        self.presence.set_available()
        self.presence.set_presence(state=PresenceState(True, PresenceShow.CHAT))
        self.presence.on_subscribe = self.on_subscribe


class BasicAgent(Agent):
    def __init__(self, name: str):
        self.logger = logging.getLogger(f'[{name}]')
        self.bot_username = name.lower()
        self.id = create_jid(name)
        self.authorized_subscriptions = [AgentType.AMS_AGENT.value, AgentType.DF_AGENT.value]
        self.role = None
        password = self.bot_username
        super().__init__(self.id, password)

    async def setup(self) -> None:
        self.add_behaviour(BasicSetupBehaviour())
