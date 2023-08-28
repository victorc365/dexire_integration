from mas.agents.basic_agent import BasicAgent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour


class SetupPresenceListener(OneShotBehaviour):
    def on_available(self, jid, stanza):
        self.agent.logger.debug(f'Agent {jid.split("@")[0]} is available.')
        print(stanza)

    def on_subscribed(self, jid):
        self.agent.logger.debug(f'Agent {jid.split("@")[0]} has accepted the subscription.')

    async def run(self):
        self.presence.on_available = self.on_available
        self.presence.on_unavailable = self.on_unavailable
        self.presence.on_subscribed = self.on_subscribed


class ListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        message = await self.receive(timeout=1)
        if message is not None:
            print(message)
            return


class DFAgent(BasicAgent):
    """Erebots implementation of FIPA Directory Facilitator (DF).

    DFAgent is responsible for keeping a list of agent providing services to which a PersonalAgent can register.

    For more information about DirectoryFacilitator in FIPA specs, please read
    http://www.fipa.org/specs/fipa00023/SC00023J.html#_Toc26668967
    """
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.add_behaviour(ListenerBehaviour())
        self.logger.debug('Setup and ready!')
        self.services = {
            'gateway': []
        }

    def register(self, agent: BasicAgent) -> None:
        print(agent.id)
        if agent.role in self.services.keys():
            self.services[agent.role].append(agent.id)
            self.presence.subscribe(agent.id)

    def unregister(self, agent: BasicAgent) -> None:
        if agent.role in self.services.keys() and agent.id in self.services[agent.role]:
            self.presence.unsubscribe(agent.id)
