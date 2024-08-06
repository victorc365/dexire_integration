import asyncio
import json
import traceback
import pickle
import pandas as pd
import typing as t
import requests
import datetime as dt
import re
import numpy as np
import requests

from spade.message import Message
from spade.behaviour import State
from http import HTTPStatus

from core.src.mas.agents.personal_agent.behaviours.contextual_fsm import AbstractContextualFSMBehaviour
from core.src.services.persistence_service import PryvPersistenceService

from modules.nvcbot.explanations import get_explanations
from modules.nvcbot.recommendations import (generate_custom_recipes,
                                            get_allergies, 
                                            get_meals, 
                                            get_recipe_classes, 
                                            get_cultural_factors, 
                                            get_flexi_diet, 
                                            get_places,
                                            get_social_situation,
                                            get_time_options)

import modules.nvcbot.recommendations.data_columns as data_cols

from modules.nvcbot.recommendations.preferences_module import process_ingredients_specs
from modules.nvcbot.recommendations.recommender_service import RecommenderService
from modules.nvcbot.db.models import *
from modules.nvcbot import CACHE_DIR, USER_PROFILES_DIR
from bs4 import BeautifulSoup

from modules.nvcbot.recommendations.user_profile import UserProfile


def get_age_range(age: int):
    age_dict = {
        "18-29": 0.10,
        "30-39": 0.10,
        "40-49": 0.10,
        "50-59": 0.20,
        "60-69": 0.20,
        "70-79": 0.10,
        "80-89": 0.10,
        "90-100": 0.10
    }
    for k in age_dict.keys():
        if int(k.split("-")[0]) <= age <= int(k.split("-")[1]):
            return k
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
    
REPLY_TIMEOUT = 600

def get_user_dict(agent_id) -> t.Dict:
    with open(USER_PROFILES_DIR /  f'{agent_id}.pkl', 'rb') as file:
        user_dict = pickle.load(file)
    return user_dict

def set_user_dict(agent_id, user_dict) -> None:
    with open(USER_PROFILES_DIR /  f'{agent_id}.pkl', 'wb') as file:
        pickle.dump(user_dict, file)
        
def get_hour_from_text(text: str) -> float:
    time = dt.datetime.now().strftime("%H.%M")
    try:
        result = re.search(r'\d+:\d+', text, re.IGNORECASE)
        groups = result.groups()
        time = f"{groups[0]}.{groups[1]}"
    except:
        print("Error processing hour from text: ", text)
    return float(time)


# Define the state machine behaviour
class AskAllergiesState(State):
    def __init__(self) -> None:
        super().__init__()
        
    async def run(self) -> None:
        await asyncio.sleep(3)
        try:
            print("SENDING ALLERGIES")
            await self.send(prep_outgoing_message(self.agent.id, "Please state your allergies."))
            system_allergies = get_allergies()
            keyboard_message = prep_keyboard_message(self.agent.id, [{"label": allergy.title(), "action": allergy} for allergy in system_allergies])
            await self.send(keyboard_message)

            allergies = []
            message = await self.receive(REPLY_TIMEOUT)
            while message.body != "CONTINUE":
                if message.body in system_allergies:
                    allergies.append(message.body)

                message = await self.receive(REPLY_TIMEOUT)

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)
                
            user_dict["allergy"] = ";".join(allergies)
            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'wb') as file:
                pickle.dump(user_dict, file)

            print("ALLERGIES DONE: ", allergies)
            self.set_next_state("askCulturalFactorState")
        except:
            traceback.print_exc()

class AskCulturalFactorState(State):
    def __init__(self) -> None:
        super().__init__()
        
    async def run(self) -> None:
        await asyncio.sleep(3)

        try: 
            print("SENDING CULTURAL FACTORS")
            await self.send(prep_outgoing_message(self.agent.id, "Do you follow some of the following diets?")) # send message
            system_eating_habits = get_cultural_factors()
            keyboard_message = prep_keyboard_message(self.agent.id, [{"label": habit.replace('_',  ' ').title(), \
                "action": habit} for habit in system_eating_habits])
            
            await self.send(keyboard_message)

            user_cultural_factors = []
            message = await self.receive(REPLY_TIMEOUT)
            while message.body != "CONTINUE" and message.body != "NONE":
                if message.body in system_eating_habits:
                    user_cultural_factors.append(message.body)
                    break
            
            message = await self.receive(REPLY_TIMEOUT)

            print("CULTURAL FACTORS: ", user_cultural_factors)

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)
            
            if len(user_cultural_factors) > 0:
                user_dict["cultural_factor"] = user_cultural_factors[0]
            else:
                user_dict["cultural_factor"] = "NotRestriction"

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'wb') as file:
                pickle.dump(user_dict, file)
                
            if "flexi_observant" in user_cultural_factors:
                self.set_next_state("askFlexiObservantState")
            else:
                self.set_next_state("askMealTypeState")

        except:
            traceback.print_exc()

class AskFlexiObservantState(State):
    def __init__(self) -> None:
        super().__init__()
        
    async def run(self) -> None:
        await asyncio.sleep(3)
        
        try: 
            print("SENDING FLEXI OBSERVANT")
            await self.send(prep_outgoing_message(self.agent.id, "Do you follow some of the following flexible diets?")) # send message
            system_eating_habits = get_flexi_diet()
            keyboard_message = prep_keyboard_message(self.agent.id, [{"label": habit, "action": habit} for habit in system_eating_habits])
            
            await self.send(keyboard_message)

            flexi_diets = []
            message = await self.receive(REPLY_TIMEOUT)
            while message.body != "CONTINUE" and message.body != "NONE":
                if message.body in system_eating_habits:
                    flexi_diets.append(message.body)
                    break
            
            message = await self.receive(REPLY_TIMEOUT)

            print("CULTURAL FACTORS: ", flexi_diets)

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)
            
            if len(flexi_diets) > 0:
                user_dict["flexi_observant"] = flexi_diets[0]
            else:
                user_dict["flexi_observant"] = "NotRestriction"

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'wb') as file:
                pickle.dump(user_dict, file)
            self.set_next_state("askMealTypeState")

        except:
            traceback.print_exc()
            
# context states 
class AskMealTypeState(State):
    def __init__(self) -> None:
        super().__init__()
        
    async def run(self) -> None:
        await asyncio.sleep(3)
        
        try:
            print("SENDING MEAL TYPE")
            await self.send(prep_outgoing_message(self.agent.id, "Which of the following meal types are you going to consume?"))
            system_meal_types = get_meals()
            keyboard_message = prep_keyboard_message(self.agent.id, [{"label": meal_type.title(), "action": meal_type} for meal_type in system_meal_types])
            
            await self.send(keyboard_message)
            
            meal_type = []
            message = await self.receive(REPLY_TIMEOUT)
            while message.body != "CONTINUE" and message.body != "NONE":
                if message.body in system_meal_types:
                    meal_type.append(message.body)
                    break
            message = await self.receive(REPLY_TIMEOUT)

            print("Meal type: ", meal_type)

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)
            
            if len(meal_type) > 0:
                user_dict["meal_type_y"] = meal_type[0]
            else:
                user_dict["meal_type_y"] = "lunch"

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'wb') as file:
                pickle.dump(user_dict, file)
            self.set_next_state("askPlaceState")
        except:
            traceback.print_exc()
            
class AskPlaceState(State):
    def __init__(self) -> None:
        super().__init__()
        
    async def run(self) -> None:
        await asyncio.sleep(3)
        
        try:
            print("SENDING PLACE")
            await self.send(prep_outgoing_message(self.agent.id, "Where are you going to eat?"))
            system_places = get_places()
            keyboard_message = prep_keyboard_message(self.agent.id, [{"label": place.title(), "action": place} for place in system_places])
            
            await self.send(keyboard_message)
            
            places = []
            message = await self.receive(REPLY_TIMEOUT)
            while message.body != "CONTINUE" and message.body != "NONE":
                if message.body in system_places:
                    places.append(message.body)
                    break
            message = await self.receive(REPLY_TIMEOUT)

            print("Meal type: ", places)

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)
            
            if len(places) > 0:
                user_dict["place_of_meal_consumption"] = places[0]
            else:
                user_dict["place_of_meal_consumption"] = "home"

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'wb') as file:
                pickle.dump(user_dict, file)
            self.set_next_state("askSocialSituationState")
        except:
            traceback.print_exc()
            
class AskSocialSituationState(State):
    def __init__(self) -> None:
        super().__init__()
        
    async def run(self) -> None:
        await asyncio.sleep(3)
        
        try:
            print("SENDING SOCIAL SITUATION")
            await self.send(prep_outgoing_message(self.agent.id, "Who are you going to eat with?"))
            system_social_situations = get_social_situation()
            keyboard_message = prep_keyboard_message(self.agent.id, [{"label": social_situation.title(), "action": social_situation} for social_situation in system_social_situations])
            
            await self.send(keyboard_message)
            
            social = []
            message = await self.receive(REPLY_TIMEOUT)
            while message.body != "CONTINUE" and message.body != "NONE":
                if message.body in system_social_situations:
                    social.append(message.body)
                    break
            message = await self.receive(REPLY_TIMEOUT)

            print("Social_situation: ", social)

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)
            
            if len(social) > 0:
                user_dict["social_situation_of_meal_consumption"] = social[0]
            else:
                user_dict["social_situation_of_meal_consumption"] = "alone"

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'wb') as file:
                pickle.dump(user_dict, file)
            self.set_next_state("askTimeState")
        except:
            traceback.print_exc()
            
class AskTimeState(State):
    def __init__(self) -> None:
        super().__init__()
        
    async def run(self) -> None:
        await asyncio.sleep(3)
        
        try:
            print("SENDING TIME")
            await self.send(prep_outgoing_message(self.agent.id, "What time are you going to eat?"))
            system_times = get_time_options()
            keyboard_message = prep_keyboard_message(self.agent.id, [{"label": time.title(), "action": time} for time in system_times])
            
            await self.send(keyboard_message)
            meal_time = 0.0
            time_option = []
            message = await self.receive(REPLY_TIMEOUT)
            while message.body != "CONTINUE" and message.body != "NONE":
                if message.body in system_times:
                    time_option.append(message.body)
                    break
            message = await self.receive(REPLY_TIMEOUT)
                
            if len(time_option) > 0:
                if time_option[0] == "other time":
                    meal_time = await self.send(prep_outgoing_message(self.agent.id, "Please enter the hour (Hour:minute am/pm)."))
                    message = await self.receive(REPLY_TIMEOUT)
                    text = message.body
                    text = text.lower()
                    meal_time = get_hour_from_text(text)
                    if "pm" in text:
                        meal_time += 12
                elif time_option[0] == "in one hour":
                    time_delta = dt.timedelta(hours=1)
                    meal_time = float((dt.datetime.now()+time_delta).strftime("%H.%M"))
                elif time_option[0] == "in two hours":
                    time_delta = dt.timedelta(hours=2)
                    meal_time = float((dt.datetime.now()+time_delta).strftime("%H.%M"))
            else:
                # default time now 
                meal_time = float(dt.datetime.now().strftime("%H.%M"))
                

            print("Meal time: ", meal_time)

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)
            
            user_dict['time_of_meal_consumption'] = meal_time


            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'wb') as file:
                pickle.dump(user_dict, file)
            self.set_next_state("askRecommendationsState")
        except:
            traceback.print_exc()
            
class AskRecommendationsState(State):
    def __init__(self) -> None:
        super().__init__()
        
    async def run(self) -> None:
        await asyncio.sleep(3)
        
        try:
            print("SENDING RECOMMENDATIONS")
            food_dataset = pd.read_csv("./modules/nvcbot/data/df_recipes.csv", index_col=0, sep="|")
            # get user_features and transform it into  dataframe 
            if os.path.exists(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl"):
                with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "rb") as fp:
                    selected = pickle.load(fp)
                print(f"received: {selected}")
            user_dict = {}
            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)
            print(f"User Dict: {user_dict}")
            if user_dict is not None:    
                user_data = {'nutrition_goal':user_dict.get("nutritional_goal", "maintain_fit"), 
                            'clinical_gender':user_dict.get("gender", "M"), 
                            'age_range': get_age_range(user_dict.get("age", 25)), 
                            'life_style':user_dict.get("life_style", "Very active"), 
                            'weight':user_dict.get("weight", 70),  
                            'height':user_dict.get("height", 170), 
                            'projected_daily_calories':user_dict.get("projected_daily_calories", 2000), 
                            'current_daily_calories': user_dict.get("current_daily_calories", 1700),
                            'cultural_factor': user_dict.get("cultural_factor", "NotRestriction"),  
                            'allergy': user_dict.get("allergy", "NotAllergy"), 
                            'current_working_status': user_dict.get("current_working_status", "Full-time-worker"), 
                            'marital_status': user_dict.get("marital_status", "Single"),  
                            'ethnicity': user_dict.get("ethnicity", "White"), 
                            'BMI': user_dict.get("BMI", "healthy"),  
                            'next_BMI':user_dict.get("next_BMI", "healthy")}  
            # get context features 
            context_features = {
                'day_number': user_dict.get("day_number", 0), 
                'meal_type_y': user_dict.get("meal_type_y", "lunch"),
                'time_of_meal_consumption': user_dict.get("time_of_meal_consumption", 12.0), 
                'place_of_meal_consumption': user_dict.get("place_of_meal_consumption", "restaurant"), 
                'social_situation_of_meal_consumption': user_dict.get("social_situation_of_meal_consumption", "alone")
            }
            prepare_data = {
                "profile": user_data,
                "context": context_features
            }
            print(f"send_data: %s" % prepare_data)
            url = "http://localhost:8500/recommendation/"
            ans = requests.post(url, json=prepare_data)
            print(f"Ans: {ans.json()}")
            # process answer 
            answer = ans.json()
            # save answer
            with open(CACHE_DIR / "interactive" / f"{self.agent.id}.pkl", "wb") as fp:
                pickle.dump(answer, fp)
            recommendations = answer["recommendations"]
            print(f"recommendations: {recommendations}")
            # recommended food 
            selected_recipes = food_dataset[food_dataset["recipeId"].isin(recommendations)]
            # get recommendation
            await self.send(prep_outgoing_message(self.agent.id, "Based on your profile, preferences, and context, here are some recipes for you."))
            print(f"System Recipes: {selected_recipes}")
            buttons = [{"label": recipe['name'].title(), "action": recipe['recipeId']} for i, recipe in selected_recipes.iterrows()]
            buttons += [{"label": f"Explain: {recipe['name'].title()}", "action": f"explain_{recipe['recipeId']}"} for i, recipe in selected_recipes.iterrows()]
            buttons += [{"label": "Get more recommendations", "action": "more_recommendations"}]
            keyboard_message = prep_keyboard_message(self.agent.id, buttons)
            await self.send(keyboard_message)
            
            message = await self.receive(REPLY_TIMEOUT)
            if message.body == "more_recommendations":
                self.set_next_state("askRecommendationsState")
                return
            elif message.body in [f"explain_{recipe['recipeId']}" for i, recipe in selected_recipes.iterrows()]:
                self.set_next_state("displayExplanationState")
                with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "wb") as fp:
                    pickle.dump(message.body, fp)
                return
            elif message.body in [recipe['recipeId'] for i, recipe in selected_recipes.iterrows()]:
                self.set_next_state("displayRecipeInfoState")
                with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "wb") as fp:
                    pickle.dump(message.body, fp)
                return
            message = await self.receive(REPLY_TIMEOUT)
            self.set_next_state("finalState")
        except:
            traceback.print_exc()
            await self.send(prep_outgoing_message(self.agent.id, "Something went wrong less try again."))
            self.set_next_state("finalState")

class DisplayRecipeState(State):
    def __init__(self) -> None:
        super().__init__()
    
    async def run(self) -> None:
        # show recipe info 
        await asyncio.sleep(3)
        try:
            # load recipes 
            food_dataset = pd.read_csv("./modules/nvcbot/data/df_recipes.csv", index_col=0, sep="|")
            # load answer 
            with open(CACHE_DIR / "interactive" / f"{self.agent.id}.pkl", "rb") as fp:
                answer = pickle.load(fp)
            # load chosen selection 
            with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "rb") as fp:
                selected = pickle.load(fp)
            selected_recipe = food_dataset[food_dataset["recipeId"] == selected]
            print(f"Recipe: {selected_recipe}")
            msg = f"Title: {selected_recipe['name']}\n {selected_recipe['ingredients']}\n {selected_recipe['instructions']}\n"
            await self.send(prep_outgoing_message(self.agent.id,
                                            msg
                                            ))
            buttons = [{"label": "Give Feedback", "action": "feedback"}, {"label": "Back", "action": "back"}]
            keyboard_message = prep_keyboard_message(self.agent.id, buttons)
            await self.send(keyboard_message)
            message = await self.receive(REPLY_TIMEOUT)
            if message.body == "feedback":
                self.set_next_state("askFeedbackState")
                return 
            elif message.body == "back":
                self.set_next_state("askRecommendedState")
                with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "wb") as fp:
                    pickle.dump(message.body, fp)
                return 
            self.set_next_state("finalState")
        except:
            traceback.format_exc()

class DisplayExplanationState(State):
    def __init__(self) -> None:
        super().__init__()
        
    async def run(self) -> None:
        try:
            # load answer 
            with open(CACHE_DIR / "interactive" / f"{self.agent.id}.pkl", "rb") as fp:
                answer = pickle.load(fp)
            print(answer)
            # load chosen selection 
            with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "rb") as fp:
                selected = pickle.load(fp)
            print(selected)
            id = selected.split("_")[-1]
            recommendations = answer["recommendations"]
            index = 0
            for i in range(len(recommendations)):
                if id == recommendations[i]:
                    index = i
                    break
            await self.send(prep_outgoing_message(self.agent.id, "Select the kind of explanation desired:"))
            buttons = [{"label": "Give Feedback", "action": "feedback"},
                       {"label": "Back", "action": "back"}, 
                       {"label": "Rule Based", "action": "rule"},
                       {"label": "Probabilistic", "action": "probabilistic"},]
            keyboard_message = prep_keyboard_message(self.agent.id, buttons)
            await self.send(keyboard_message)
            message = await self.receive(REPLY_TIMEOUT)
            
            if message.body == "feedback":
                self.set_next_state("askFeedbackState")
                return 
            elif message.body == "back":
                self.set_next_state("askRecommendedState")
                with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "wb") as fp:
                    pickle.dump(message.body, fp)
                return 
            elif message.body == "rule":
                expa = answer["rule_based_explanation"][index]
                await self.send(prep_outgoing_message(self.agent.id, expa))
                with open(CACHE_DIR / "interactive" / f"{self.agent.id}_xai.pkl", "wb") as fp:
                    pickle.dump({"xai_type":message.body, "xai_text": expa}, fp)
                self.set_next_state("askFeedbackState")
                return
            elif message.body == "probabilistic":
                expa = answer["probabilistic_explanation"][index]
                await self.send(prep_outgoing_message(self.agent.id, expa))
                with open(CACHE_DIR / "interactive" / f"{self.agent.id}_xai.pkl", "wb") as fp:
                    pickle.dump({"xai_type":message.body, "xai_text": expa}, fp)
                self.set_next_state("askFeedbackState")
                return
            self.set_next_state("finalState")
        except:
            traceback.format_exc()
            
class AskFeedBack(State):
    def __init__(self) -> None:
        super().__init__()
        
    async def run(self) -> None:
        await asyncio.sleep(3)
        try:
            with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "rb") as fp:
                selected = pickle.load(fp)
            print(selected)
            await self.send(prep_outgoing_message(self.agent.id, "would you like to provide feedback:"))
            message = await self.receive(REPLY_TIMEOUT)
            with open(CACHE_DIR / "interactive" / f"{self.agent.id}_feedback.pkl", "wb") as fp:
                pickle.dump({"feedback_text": message.body, "recipe": selected}, fp)
            self.set_next_state("finalState")
        except:
            traceback.format_exc()
        

# old states ---------------------------------------------------------------
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

        self.add_state(name="askAllergiesState",
                       state=AskAllergiesState(),
                       initial=True)
        self.add_state(name="askCulturalFactorState",
                       state=AskCulturalFactorState())
        self.add_state(name="askMealTypeState",
                       state=AskMealTypeState())
        self.add_state(name="askFlexiObservantState",
                       state=AskFlexiObservantState())
        self.add_state(name="askPlaceState",
                       state=AskPlaceState())
        self.add_state(name="askSocialSituationState",
                       state=AskSocialSituationState())
        self.add_state(name="askTimeState",
                       state=AskTimeState())
        self.add_state(name="askRecommendationsState",
                       state=AskRecommendationsState())
        self.add_state(name="recipeFeedbackState",
                       state=RecipeFeedbackState())
        self.add_state(name="explanationFeedbackState",
                       state=ExplanationFeedbackState())
        self.add_state(name="finalState",
                       state=FinalState())
        self.add_state(name="displayRecipeState",
                       state=DisplayRecipeState())
        self.add_state(name="displayExplanationState",
                       state=DisplayExplanationState())
        self.add_state(name="askFeedbackState",
                       state=AskFeedBack())
        
        self.add_transition("askAllergiesState", "askCulturalFactorState")
        self.add_transition("askCulturalFactorState", "askMealTypeState")
        self.add_transition("askCulturalFactorState", "askFlexiObservantState")
        self.add_transition("askFlexiObservantState", "askMealTypeState")
        self.add_transition("askMealTypeState", "askPlaceState")
        self.add_transition("askPlaceState", "askSocialSituationState")
        self.add_transition("askSocialSituationState", "askTimeState")
        self.add_transition("askTimeState", "askRecommendationsState")
        self.add_transition("askRecommendationsState", "finalState")
        self.add_transition("askRecommendationsState", "displayRecipeState")
        self.add_transition("askRecommendationsState", "displayExplanationState")
        self.add_transition("displayRecipeState", "askRecommendationsState")
        self.add_transition("displayExplanationState", "askRecommendationsState")
        self.add_transition("displayRecipeState", "askFeedbackState")
        self.add_transition("displayExplanationState", "askFeedbackState")
        self.add_transition("displayRecipeState", "finalState")
        self.add_transition("displayExplanationState", "finalState")
        self.add_transition("askFeedbackState", "finalState")
        self.add_transition("askRecommendationsState", "askRecommendationsState")
        self.add_transition("finalState", "askRecommendationsState")
        
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
            # load recipes dataset
            dataset = pd.read_csv("./modules/nvcbot/data/df_recipes.csv", index_col=0, sep="|")
            print("dataset loaded with shape: ", dataset.shape)
            print("pryv: ", pryv_profile)
            user_data = {
                "user_name": pryv_profile.get("name", "UserName"),
                "gender": pryv_profile.get("gender", "male"),
                "age": int(pryv_profile.get("age", "33")),
                "weight": int(pryv_profile.get("weight", "70")),
                "height": int(pryv_profile.get("height", "170")),
                "working_status": pryv_profile.get("working_status", "Full-time-worker"),
                "marital_status": pryv_profile.get("marital_status", "Married"),
                "life_style": pryv_profile.get("life_style", "Very active"),
                "nutritional_goal": pryv_profile.get("nutritional_goal", "maintain_fit") 
            }
            # load user data model and process data 
            user_profiler = UserProfile(user_data)
            user_profiler.calculate_bmi()
            user_profiler.basal_metabolic_rate()
            user_profiler.current_daily_calories = user_profiler.calculate_daily_calorie_needs(
                user_profiler.bmr,
                user_profiler.life_style
                )  
            user_profiler.projected_daily_calories = user_profiler.projected_calorie_needs()                                                       
            complete_user_data = vars(user_profiler)
            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'wb') as file:
                pickle.dump(complete_user_data, file)
        except Exception as exe:
            traceback.print_exc()

