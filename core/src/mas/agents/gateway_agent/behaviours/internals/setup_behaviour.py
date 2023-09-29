from spade.behaviour import OneShotBehaviour
from services.bot_service import BotService
from enums.environment import Environment
import os


class SetupBehaviour(OneShotBehaviour):
    def on_subscribe(self, jid):
        subscriber = jid.split("@")[0]
        self.agent.logger.debug(f'Agent {subscriber} asked for subscription.')
        bot_name = subscriber.split('_')[0]
        if bot_name in BotService().get_bots():
            number_clients = len(self.agent.clients.keys())
            maximum_clients = int(os.environ.get(Environment.MAXIMUM_CLIENTS_PER_GATEWAY.value))
            if number_clients >= maximum_clients:
                return
            self.agent.clients[subscriber] = None
            self.presence.subscribe(jid)
        self.agent.logger.info(f'Subscription from  {subscriber} approved.')
        self.presence.approve(jid)

    async def run(self):
        self.presence.on_subscribe = self.on_subscribe
