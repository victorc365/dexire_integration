from mas.agents.basic_agent import BasicAgent
from mas.enums.performative import Performative
from mas.core_engine import CoreEngine
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
import json


class AvailableGatewayRequestMessage(Message):
    def __init__(self, sender: str) -> None:
        super().__init__(
            to=CoreEngine().df_agent.id,
            sender=sender,
            metadata={Performative.PERFORMATIVE.value: Performative.REQUEST.value}
        )


class ListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        message = await self.receive(timeout=1)
        if message is None:
            return

        if message.metadata[Performative.PERFORMATIVE.value] == Performative.AGREE.value:
            gateways = json.loads(message.body)
            for gateway in gateways:
                if any(gateway == str(contact) for contact in self.presence.get_contacts()):
                    # Todo - Use an already known gateway
                    pass
                else:
                    # Use the most recent gateway as it should have available space
                    last_gateway = gateways[-1]
                    self.presence.subscribe(last_gateway)


class RegisterToGatewayBehaviour(OneShotBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        # ask DF for available non full gateway
        message = AvailableGatewayRequestMessage(self.agent.id)
        await self.send(message)


class PersonalAgent(BasicAgent):
    def __init__(self, bot_user_name: str, password: str, token: str):
        super().__init__(bot_user_name)
        self.password = password
        self.token = token

    async def setup(self):
        self.logger.debug('Setup and ready!')
        await super().setup()
        self.add_behaviour(RegisterToGatewayBehaviour())
        self.add_behaviour(ListenerBehaviour())
