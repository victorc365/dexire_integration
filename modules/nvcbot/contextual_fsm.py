import asyncio
from spade.message import Message
from spade.behaviour import State
from http import HTTPStatus

from core.src.mas.agents.personal_agent.behaviours.contextual_fsm import AbstractContextualFSMBehaviour
from core.src.services.persistence_service import PryvPersistenceService
from core.src.services.chat_service import ChatService

import pandas as pd

import traceback

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

### temp state until magic keyboard
class InitialState(State):
    def __init__(self) -> None:
        super().__init__()

        self.next_state = "echoState"

    async def run(self) -> None:
        await asyncio.sleep(5)
        
        init_message = Message()
        init_message.sender = self.agent.id
        init_message.to = "gateway_agent_1@localhost"
        init_message.thread = "user-thread"
        init_message.body = "Please state your allergies. (Peanuts or Yoghurt)"
        init_message.metadata = {'performative': 'inform', 'direction': 'outgoing', 'target': 'hemerapp',
                          'context': 'contextual', 'body_format': 'text'}

        await self.send(init_message)

        message = await self.receive()

        # message contains the allergies

        print(message)
        try: 

            from modules.nvcbot.recommendations import generate_custom_recipes
            import json

            persistence_service: PryvPersistenceService = self.agent.persistence_service
            def get_user_health_scores(persistence_service: PryvPersistenceService):
                import requests

                url = f'{persistence_service.url}/events'
                params = {
                    'streams': f'{persistence_service.module_name}_healthscores'
                }

                response = requests.get(url, params=params, headers={'authorization': persistence_service.token})

                if response.status_code != HTTPStatus.OK:
                    raise Exception(f'Exception while getting profile: {response.status_code}/{response.text}')
                data = response.json()
                events = data['events']
                if len(events) == 0:
                    return {}

                return events[0]['content']

            pryv_profile = json.loads(persistence_service.get_profile())
            health_scores = json.loads(get_user_health_scores(persistence_service))


            ## TO DO: Revise interactive. Are we having traditional vs interactive here too?
            generate_custom_recipes(self.agent.id, pryv_profile, health_scores, "interactive")
        except:
            traceback.print_exc()

        reply = Message(),
        reply.to = str(message.sender)
        reply.sender = str(message.to)
        reply.metadata = {'performative': 'inform', 'direction': 'outgoing', 'target': 'hemerapp',
                          'context': 'contextual', 'body_format': 'text'}
        
        reply.body = "Please state your allergies. (Peanuts or Yoghurt)"

        await self.send(reply)

class RecommendationState(State):
    ...

class ContextualFSM(AbstractContextualFSMBehaviour):
    def __init__(self):
        super().__init__()

    def setup(self):
        super().setup()

        self.add_state(name="initialState",
                       state=InitialState(),
                       initial=True)
        self.add_state(name="echoState",
                       state=EchoState())
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

