import asyncio
from spade.message import Message
from spade.behaviour import State
from core.src.mas.agents.personal_agent.behaviours.contextual_fsm import AbstractContextualFSMBehaviour
from core.src.services.persistence_service import PryvPersistenceService
import pandas as pd


class EchoState(State):
    def __init__(self) -> None:
        super().__init__()
        self.next_state = "echoState"

    async def run(self) -> None:
        while self.mailbox_size() == 0:
            await asyncio.sleep(1)
        message = await self.receive()
        reply = Message()
        reply.thread = message.thread
        reply.to = str(message.sender)
        reply.sender = str(message.to)
        reply.metadata = {'performative': 'inform', 'direction': 'outgoing', 'target': 'hemerapp',
                          'context': 'contextual'}
        reply.body = message.body
        await self.send(reply)

class RecommendatationState(State):
    def __init__(self):
        super().__init__()
        self.next_state = ""


class ContextualFSM(AbstractContextualFSMBehaviour):
    def __init__(self):
        super().__init__()

    def setup(self):
        super().setup()

        self.add_state(name="echoState",
                       state=EchoState(),
                       initial=True)
        self.add_transition("echoState", "echoState")

    async def on_start(self):
        self.agent.logger.debug("STARTED.")
        persistence_service: PryvPersistenceService = self.agent.persistence_service
        pryv_profile = persistence_service.get_profile()
        self.agent.logger.debug("PRYV PROF: ", pryv_profile)

        from recommendations.health_module import HealthModule
        dataset = pd.read_excel("./data/diyetkolik_recipes.xlsx", index_col=0)

        user_data = {
            "weight": 100,
            "height": 180,
            "age": 25,
            "gender": "male",
            "sports": "sedentary",
            "mealtype": "dinner",
        }

        health_module = HealthModule(user_data)

        user_bmr = health_module.bmr()
        user_amr = health_module.amr()

        health_scores = health_module.calculate_scores(dataset)
        user_data["healthscores"] = health_scores.to_json()
        user_data["bmr"] = user_bmr
        user_data["amr"] = user_amr

        persistence_service.save_data(user_data, "healthscores")
        self.agent.logger.debug("INIT COMPLETE")

        await super().on_start()
