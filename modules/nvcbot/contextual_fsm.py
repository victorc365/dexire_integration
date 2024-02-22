import asyncio
import json
import traceback
import pickle
import pandas as pd
import typing as t
import requests

from spade.message import Message
from spade.behaviour import State
from http import HTTPStatus

from core.src.mas.agents.personal_agent.behaviours.contextual_fsm import AbstractContextualFSMBehaviour
from core.src.services.persistence_service import PryvPersistenceService

from modules.nvcbot.explanations import get_explanations
from modules.nvcbot.recommendations import generate_custom_recipes, get_allergies, get_eating_habits, get_recipe_classes
from modules.nvcbot.recommendations.preferences_module import process_ingredients_specs
from modules.nvcbot.recommendations.health_module import HealthModule
from modules.nvcbot.db.models import *
from modules.nvcbot import CACHE_DIR, USER_PROFILES_DIR
from bs4 import BeautifulSoup


def get_google_image(query):
    url = f"https://www.google.com/search?q={query}&tbm=isch" 
    response = requests.get(url) 
    soup = BeautifulSoup(response.text, "html.parser") 

    img_tag = soup.find("img", {"class": "yWs4tf"})
    if img_tag is not None:
        img_link = img_tag.get("src")
        return img_link
    else:
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Good_Food_Display_-_NCI_Visuals_Online.jpg/1920px-Good_Food_Display_-_NCI_Visuals_Online.jpg"

def prep_keyboard_message(agent_id, buttons: list) -> Message:
    keyboard_message = prep_outgoing_message(agent_id, json.dumps({"items": buttons}), "keyboard")
    return keyboard_message

def prep_outgoing_message(agent_id, body, context="contextual", body_format="text"):
    message = Message()
    message.sender = agent_id
    message.to = "gateway_agent_1@localhost"
    message.thread = "user-thread"
    message.metadata = {'performative': 'inform', 'direction': 'outgoing', 'target': 'hemerapp',
                            'context': context, 'body_format': body_format}
    message.body = body

    return message
    
REPLY_TIMEOUT = 60

def get_user_dict(agent_id) -> t.Dict:
    with open(USER_PROFILES_DIR /  f'{agent_id}.pkl', 'rb') as file:
        user_dict = pickle.load(file)
    return user_dict

def set_user_dict(agent_id, user_dict) -> None:
    with open(USER_PROFILES_DIR /  f'{agent_id}.pkl', 'wb') as file:
        pickle.dump(user_dict, file)


class EatingHabitsState(State):
    def __init__(self) -> None:
        super().__init__()

    async def run(self) -> None:
        await asyncio.sleep(3)

        try: 
            print("SENDING EATING HABITS")
            await self.send(prep_outgoing_message(self.agent.id, "Please state your eating habits.")) # send message
            system_eating_habits = get_eating_habits()
            keyboard_message = prep_keyboard_message(self.agent.id, [{"label": habit.title(), "action": habit} for habit in system_eating_habits])
            
            await self.send(keyboard_message)

            user_eating_habits = []
            message = await self.receive(REPLY_TIMEOUT)
            while message.body != "CONTINUE" and message.body != "NONE":
                if message.body in system_eating_habits:
                    user_eating_habits.append(message.body)

                message = await self.receive(REPLY_TIMEOUT)

            print("EATING HABITS DONE: ", user_eating_habits)

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)
            
            user_dict["eating_habits"] = user_eating_habits

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'wb') as file:
                pickle.dump(user_dict, file)

            self.set_next_state("allergyState")

        except:
            traceback.print_exc()

class AllergyState(State):
    async def run(self) -> None:
        try: 
            print("SENDING ALLERGIES")
            await self.send(prep_outgoing_message(self.agent.id, "Please state your allergies."))
            system_allergies = get_allergies()
            keyboard_message = prep_keyboard_message(self.agent.id, [{"label": allergy, "action": allergy} for allergy in system_allergies])
            await self.send(keyboard_message)

            allergies = []
            message = await self.receive(REPLY_TIMEOUT)
            while message.body != "CONTINUE":
                if message.body in system_allergies:
                    allergies.append(message.body)

                message = await self.receive(REPLY_TIMEOUT)

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)

            user_dict["allergies"] = allergies
            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'wb') as file:
                pickle.dump(user_dict, file)

            print("ALLERGIES DONE: ", allergies)
            self.set_next_state("dislikedItemsState")

        except:
            traceback.print_exc()

class IngredientPreferenceState(State):
    preference_type: str

    async def run(self) -> None:
        await self.send(prep_outgoing_message(self.agent.id, f"Please state the foods you {self.preference_type}."))

        try: 
            system_recipe_classes = get_recipe_classes()
            keyboard_message = prep_keyboard_message(self.agent.id, [{"label": recipe_class, "action": recipe_class} for recipe_class in system_recipe_classes])
            await self.send(keyboard_message)

            user_recipe_classes = []
            message = await self.receive(REPLY_TIMEOUT)
            while message.body != "CONTINUE":
                if message.body in system_recipe_classes:
                    user_recipe_classes.append(message.body)

                message = await self.receive(REPLY_TIMEOUT)
            

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)
                user_dict[f"{self.preference_type}_classes"] = user_recipe_classes
            
            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'wb') as file:
                pickle.dump(user_dict, file)

        except:
            traceback.print_exc()

class DislikedItemsState(IngredientPreferenceState):
    def __init__(self):
        super().__init__()
        self.preference_type = "dislike"
    async def run(self) -> None:
        await super().run()
        self.set_next_state("likedItemsState")

class LikedItemsState(IngredientPreferenceState):
    def __init__(self):
        super().__init__()
        self.preference_type = "like"
    async def run(self) -> None:
        await super().run()
        self.set_next_state("internalCalculationsState")


class InternalCalculationsState(State):
    async def run(self) -> None:
        print("Running calculations...")
        persistence_service: PryvPersistenceService = self.agent.persistence_service

        def get_user_health_scores(persistence_service: PryvPersistenceService):
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

        try:
            pryv_profile = json.loads(persistence_service.get_profile())
            health_scores = json.loads(get_user_health_scores(persistence_service))

            ## TO DO: Revise interactive. Are we having traditional vs interactive here too?
            health_scores["healthscores"] = json.loads(health_scores["healthscores"])
            
            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)

            pryv_profile["habits"] = user_dict["eating_habits"]
            generate_custom_recipes(self.agent.id, pryv_profile, health_scores, "interactive")
            process_ingredients_specs(self.agent.id, user_dict["like_classes"], user_dict["dislike_classes"])

            UserSpecificationLogs(**{"uuid": self.agent.id, "user_data": json.dumps(user_dict)}).save()

            print("calculations done!")
        except:
            traceback.print_exc()
        
        self.set_next_state("recommendationState")

class RecommendationState(State):
    async def run(self) -> None:
        print("Recommendation state:")
        try:
            cached_dataset_dir: pd.DataFrame = CACHE_DIR / "interactive" / f"{self.agent.id}.pkl"
            cached_dataset = pd.read_pickle(cached_dataset_dir)

            max_row = cached_dataset.loc[cached_dataset.recommended != -1].nlargest(1, 'total_score')

            recipe_idx = max_row.index[0]

            cached_dataset.at[recipe_idx, "recommended"] = -1
            cached_dataset.to_pickle(cached_dataset_dir)
            
            max_row = max_row.loc[recipe_idx]
            
            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)

            explanations = get_explanations(self.agent.id, max_row)


            recipe_info = max_row.to_dict()
            recipe_info["recommendation_tags"] = list(recipe_info["recommendation_tags"])
            offer_log_dict = {
                "uuid": self.agent.id,
                "recipe_info": recipe_info,
                "explanation": ";".join([item["content"] for item in explanations])
            }

            await self.send(prep_outgoing_message(self.agent.id, max_row["title"])) # send message
            await self.send(prep_outgoing_message(self.agent.id, max_row["ingredients"]))

            if user_dict["explanation_pref"]:
                await self.send(prep_outgoing_message(self.agent.id, explanations[0]["content"]))

            def get_recommendation_actions() -> list:
                return [
                    {"label": "Accept", "action": "ACCEPT"},
                    {"label": "Deny", "action": "DENY"},
                    {"label": "Photo", "action": "IMAGE"},
                    {"label": "More explanation", "action": "MORE_EXPLANATION"},
                    {"label": "How to cook?", "action": "MORE_INFO"},
                ]

            keyboard_message = prep_keyboard_message(self.agent.id, get_recommendation_actions())
            await self.send(keyboard_message)

            reply = await self.receive(REPLY_TIMEOUT)
    

            while True:
                if reply.body == "ACCEPT":
                    OfferRoundLogs(**{"action": "ACCEPT", **offer_log_dict}).save()
                    self.set_next_state("finalState")
                    break

                elif reply.body == "DENY":
                    OfferRoundLogs(**{"action": "DENY", **offer_log_dict}).save()
                    self.set_next_state("denyState")
                    break

                elif reply.body == "MORE_INFO":
                    OfferRoundLogs(**{"action": "MORE_INFO", **offer_log_dict}).save()
                    await self.send(prep_outgoing_message(self.agent.id, max_row["preparation"]))

                elif reply.body == "MORE_EXPLANATION":
                    OfferRoundLogs(**{"action": "MORE_EXPLANATION", **offer_log_dict}).save()
                    await self.send(prep_outgoing_message(self.agent.id, explanations[1]["content"]))
                    await self.send(prep_outgoing_message(self.agent.id, explanations[1]["expanded"]))

                elif reply.body == "IMAGE":
                    OfferRoundLogs(**{"action": "IMAGE", **offer_log_dict}).save()
                    await self.send(prep_outgoing_message(self.agent.id, get_google_image(max_row["title"]), body_format="image"))

                reply = await self.receive(REPLY_TIMEOUT)

        except:
            traceback.print_exc()

class DenyState(State):
    async def run(self) -> None:
        await self.send(prep_outgoing_message(self.agent.id, "Would you like to give feedback?")) # send message

        def get_feedback_actions() -> list:
            return [
                {"label": "Yes, for the recipe", "action": "RECIPE"},
                {"label": "Yes, for the explanation", "action": "EXPLANATION"},
                {"label": "No", "action": "NO_FEEDBACK"},
            ]

        keyboard_message = prep_keyboard_message(self.agent.id, get_feedback_actions())
        await self.send(keyboard_message)

        reply = await self.receive(REPLY_TIMEOUT)

        self.set_next_state(
            {"RECIPE": "recipeFeedbackState", 
             "EXPLANATION": "explanationFeedbackState", 
             "NO_FEEDBACK": "recommendationState"}[reply.body])

class FeedbackState(State):
    feedback_type: str
    feedback_questions: dict
    
    async def run(self):
        def feedback_items() -> list:
            return [{"label": label, "action": action} for action, label in self.feedback_questions.items()] 
        
        while True: 
            await self.send(prep_outgoing_message(self.agent.id, f"What would you like to say about the {self.feedback_type}?")) # send message
            await self.send(prep_keyboard_message(self.agent.id, feedback_items()))

            reply = await self.receive(REPLY_TIMEOUT)
            action = reply.body

            last_row = OfferRoundLogs.select().where(OfferRoundLogs.uuid == self.agent.id).order_by(OfferRoundLogs.id.desc()).limit(1).first()

            feedback_results = await self.feedback_action(last_row.recipe_info)

            FeedbackLogs(**{"uuid": self.agent.id,
                            "offer_id": last_row.id,
                            "feedback_type": self.feedback_type,
                            "feedback": str([action, *feedback_results])}).save()

            await self.send(prep_outgoing_message(self.agent.id, f"Would you like to give another feedback?")) # send message
            await self.send(prep_keyboard_message(self.agent.id, [{"label": "Yes", "action": "YES"}, {"label": "No", "action": "NO"}]))
            
            reply = await self.receive(REPLY_TIMEOUT)
            if reply.body == "NO":
                self.set_next_state("recommendationState")
            else:
                self.set_next_state("denyState")
            
            break

    
    async def feedback_action(self, recipe_info) -> list:
        ...

class RecipeFeedbackState(FeedbackState):
    def __init__(self):
        super().__init__()
        self.feedback_type = "recipe"
        self.feedback_questions = {"NO_LIKE": "I don't like ...",
                                   "ALLERGIC": "I'm allergic to ...",
                                   "RECENTLY_EATEN": "I ate the following recently...",
                                   }
    
    async def feedback_action(self, recipe_info) -> None:
        await self.send(prep_outgoing_message(self.agent.id, f"Which of the ingredients?")) # send message
        
        list_of_ingredients = recipe_info["ingredients_list"]
        await self.send(prep_keyboard_message(self.agent.id, [{"label": ingredient, "action": ingredient} for ingredient in list_of_ingredients.split(", ")]))

        filter_ingredients = []
        reply = await self.receive(REPLY_TIMEOUT)
        while reply.body != "CONTINUE": 
            filter_ingredients.append(reply.body)
            reply = await self.receive(REPLY_TIMEOUT)

        process_ingredients_specs(self.agent.id, None, filter_ingredients)
        return filter_ingredients


class ExplanationFeedbackState(FeedbackState):
    def __init__(self):
        super().__init__()
        self.feedback_type = "explanation"
        self.feedback_questions = {"NOT_CONVINCING": "The explanation is not convincing.",
                                   "NOT_FITTING": "The explanation doesn't fit my case.",
                                   "NOT_CLEAR": "The explanation is not clear enough.",
                                   "NOT_COMPLETE": "The explanation is incomplete."
                                   }

    async def feedback_action(self, recipe_info) -> list:
        return []

class FinalState(State):
    async def run(self) -> None:
        await self.send(prep_outgoing_message(self.agent.id, "Thanks! We hope you will enjoy this recipe.")) # send message
        await self.send(prep_outgoing_message(self.agent.id, "Would you like to receive another recipe?")) # send message

        def get_feedback_actions() -> list:
            return [
                {"label": "Yes", "action": "YES"},
                {"label": "No", "action": "NO"},
            ]

        keyboard_message = prep_keyboard_message(self.agent.id, get_feedback_actions())
        await self.send(keyboard_message)

        reply = await self.receive(REPLY_TIMEOUT)

        self.set_next_state(
            {"RECIPE": "recipeFeedbackState", 
             "NO_FEEDBACK": "recommendationState"}[reply.body])

class ContextualFSM(AbstractContextualFSMBehaviour):
    def __init__(self):
        super().__init__()

    def setup(self):
        super().setup()

        self.add_state(name="eatingHabitsState",
                       state=EatingHabitsState(),
                       initial=True)
        self.add_state(name="allergyState",
                       state=AllergyState())
        self.add_state(name="dislikedItemsState",
                       state=DislikedItemsState())
        self.add_state(name="likedItemsState",
                       state=LikedItemsState())
        self.add_state(name="internalCalculationsState",
                       state=InternalCalculationsState())
        self.add_state(name="recommendationState",
                       state=RecommendationState())
        self.add_state(name="denyState",
                       state=DenyState())
        self.add_state(name="recipeFeedbackState",
                       state=RecipeFeedbackState())
        self.add_state(name="explanationFeedbackState",
                       state=ExplanationFeedbackState())
        self.add_state(name="finalState",
                       state=FinalState())
        
        self.add_transition("eatingHabitsState", "allergyState")
        self.add_transition("allergyState", "dislikedItemsState")
        self.add_transition("dislikedItemsState", "likedItemsState")
        self.add_transition("likedItemsState", "internalCalculationsState")
        self.add_transition("internalCalculationsState", "recommendationState")

        self.add_transition("recommendationState", "finalState")
        self.add_transition("recommendationState", "denyState")

        self.add_transition("denyState", "recipeFeedbackState")
        self.add_transition("denyState", "explanationFeedbackState")

        self.add_transition("recipeFeedbackState", "denyState")
        self.add_transition("explanationFeedbackState", "denyState")

        self.add_transition("denyState", "recommendationState")
        self.add_transition("recipeFeedbackState", "recommendationState")
        self.add_transition("explanationFeedbackState", "recommendationState")

        self.add_transition("finalState", "recommendationState")


    async def on_start(self):
        await super().on_start()

        try: 
            persistence_service: PryvPersistenceService = self.agent.persistence_service
            pryv_profile = json.loads(persistence_service.get_profile())
            dataset = pd.read_csv("./modules/nvcbot/data/df_final_7000_with_classes.csv", index_col=0)
            print("pryv: ", pryv_profile)
            user_data = {
                "weight": int(pryv_profile["weight"]),
                "height": int(pryv_profile["height"]),
                "age": int(pryv_profile["age"]),
                "gender": pryv_profile["gender"],
                "sports": pryv_profile["sports"],
                "mealtype": "dinner", # Always dinner for now. TO DO: Think about this.
            }

            health_module = HealthModule(user_data)

            user_bmr = health_module.bmr()
            user_amr = health_module.amr()
            target_profile = {
                "carbs": 0.2,
                "fiber": 0.35,
                "fat": 0.1,
                "protein": 0.35,
                "calories": 1
            }
            health_scores = health_module.calculate_scores(dataset, target_profile)
            user_data["healthscores"] = health_scores.to_json()
            user_data["bmr"] = user_bmr
            user_data["amr"] = user_amr

            persistence_service.save_data(user_data, "healthscores")

            user_dict = {"explanation_pref": pryv_profile["explanation_pref"]}
            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'wb') as file:
                pickle.dump(user_dict, file)

        except Exception as exe:
            traceback.print_exc()

