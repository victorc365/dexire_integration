from mas.agents.basic_agent import BasicAgent, AgentType
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from mas.core_engine import CoreEngine
from mas.enums.performative import Performative
from enums.environment import Environment
import os


class ListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        message = await self.receive(timeout=1)
        if message is None:
            return

        if message.metadata[Performative.PERFORMATIVE.value] == Performative.REQUEST.value:
            print(message)


class SetupBehaviour(OneShotBehaviour):
    def on_subscribe(self, jid):
        subscriber = jid.split("@")[0]
        self.agent.logger.debug(f'Agent {subscriber} asked for subscription.')
        if any(authorized in subscriber for authorized in self.agent.authorized_subscriptions):
            if AgentType.PERSONAL_AGENT.value in subscriber:
                if len(self.clients) < int(os.environ.get(Environment.MAXIMUM_CLIENTS_PER_GATEWAY.value)):
                    self.clients.append(subscriber)
                    self.presence.subscribe(subscriber)

                else:
                    return
            self.agent.logger.info(f'Subscription from  {subscriber} approved.')
            self.presence.approve(jid)
        else:
            self.agent.logger.warning(f'Agent {subscriber} is not authorized for subscription.')

    async def run(self):
        self.presence.on_subscribe = self.on_subscribe


class GatewayAgent(BasicAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.role = AgentType.GATEWAY_AGENT.value
        self.authorized_subscriptions.append(AgentType.PERSONAL_AGENT.value)
        self.clients = []

    async def setup(self) -> None:
        await super().setup()
        self.add_behaviour(ListenerBehaviour())
        CoreEngine().df_agent.register(self)
        self.logger.debug('Setup and ready!')
