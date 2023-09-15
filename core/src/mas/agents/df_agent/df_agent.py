from mas.agents.basic_agent import BasicAgent
from mas.agents.df_agent.behaviours.internals.internal_listener_behaviour import InternalListenerBehaviour


class DFAgent(BasicAgent):
    """Erebots implementation of FIPA Directory Facilitator (DF).

    DFAgent is responsible for keeping a list of agent providing services to which a PersonalAgent can register.

    For more information about DirectoryFacilitator in FIPA specs, please read
    http://www.fipa.org/specs/fipa00023/SC00023J.html#_Toc26668967
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.services = {
            'gateway': []
        }

    async def setup(self) -> None:
        self.add_behaviour(InternalListenerBehaviour())
        self.logger.debug('Setup and ready!')

    def register(self, agent: BasicAgent) -> None:
        if agent.role in self.services.keys():
            self.services[agent.role].append(agent.id)
            self.presence.subscribe(agent.id)

    def unregister(self, agent: BasicAgent) -> None:
        if agent.role in self.services.keys() and agent.id in self.services[agent.role]:
            self.presence.unsubscribe(agent.id)
