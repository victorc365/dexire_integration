from spade.behaviour import OneShotBehaviour

from enums.status import Status
from mas.agents.basic_agent import AgentType
from services.chat_service import ChatService


class SetupBehaviour(OneShotBehaviour):
    def on_subscribe(self, jid):
        subscriber = jid.split("@")[0]
        self.agent.logger.debug(f'Agent {subscriber} asked for subscription.')

        if AgentType.GATEWAY_AGENT.value in subscriber:
            self.agent.logger.info(f'Subscription from  {subscriber} approved.')
            self.presence.approve(jid)
            ChatService().register_gateway(jid, self.agent.id)
            self.agent.status = Status.RUNNING.value

    async def run(self):
        self.presence.on_subscribe = self.on_subscribe
