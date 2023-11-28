import asyncio
from spade.message import Message
from spade.behaviour import State
from core.src.mas.agents.personal_agent.behaviours.contextual_fsm import AbstractContextualFSMBehaviour
from core.src.services.persistence_service import PryvPersistenceService
import pandas as pd

class RecommendatationState(State):
    def __init__(self):
        super().__init__()
        self.next_state = ""


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

class InitialState(State):
    def __init__(self) -> None:
        super().__init__()
        self.next_state = "echoState"

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
        await super().on_start()

        persistence_service: PryvPersistenceService = self.agent.persistence_service

        import json
        pryv_profile = json.loads(persistence_service.get_profile())

        dataset = pd.read_excel("./modules/nvcbot/data/diyetkolik_recipes.xlsx", index_col=0)
        try: 
            user_data = {
                "weight": int(pryv_profile["weight"]),
                "height": int(pryv_profile["height"]),
                "age": int(pryv_profile["age"]),
                "gender": pryv_profile["gender"],
                "sports": pryv_profile["sports"],
                "mealtype": "dinner", # Always dinner for now. TO DO: Think about this.
            }

            from modules.nvcbot.recommendations.health_module import HealthModule

            health_module = HealthModule(user_data)

            user_bmr = health_module.bmr()
            user_amr = health_module.amr()

            health_scores = health_module.calculate_scores(dataset)
            user_data["healthscores"] = health_scores.to_json()
            user_data["bmr"] = user_bmr
            user_data["amr"] = user_amr

            persistence_service.save_data(user_data, "healthscores")

        except Exception as exe:
            print(exe)

