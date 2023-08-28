from spade.presence import ContactNotFound

from mas.agents.basic_agent import BasicAgent
from spade.behaviour import OneShotBehaviour


class SetupPresenceListener(OneShotBehaviour):
    def on_available(self, jid, stanza):
        self.agent.logger.debug(f'Agent {jid.split("@")[0]} is available.')

    def on_subscribed(self, jid):
        self.agent.logger.debug(f'Agent {jid.split("@")[0]} has accepted the subscription.')

    async def run(self):
        self.presence.set_available()
        self.presence.on_available = self.on_available
        self.presence.on_subscribed = self.on_subscribed


class CreateAgentBehaviour(OneShotBehaviour):
    def __init__(self, new_agent: BasicAgent) -> None:
        super().__init__()
        self.new_agent = new_agent

    async def run(self) -> None:
        try:
            self.agent.presence.get_contact(self.new_agent.jid)
        except ContactNotFound:
            self.agent.logger.info(f'{self.new_agent.id} not available yet. Starting the bot')
            await self.new_agent.start(auto_register=True)
            self.presence.subscribe(self.new_agent.id)


class AMSAgent(BasicAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    async def setup(self) -> None:
        await super().setup()
        self.add_behaviour(SetupPresenceListener())

    async def create_agent(self, agent: BasicAgent) -> None:
        self.add_behaviour(CreateAgentBehaviour(agent))
