import asyncio
from spade.message import Message
from spade.behaviour import State
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
from bs4 import BeautifulSoup

from core.src.services.persistence_service import PryvPersistenceService

from modules.nvcbot import CACHE_DIR, USER_PROFILES_DIR
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

REPLY_TIMEOUT = 600

# Functions utilities 
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

def get_time_from_text(text: str) -> float:
    try:
        pattern = r'\d+:\d+'
        time_str_list = re.findall(pattern, text)
        if len(time_str_list) >= 1:
            temp_str = time_str_list[0].split(':')
            hour = int(temp_str[0])
            minute = int(temp_str[1])
        else:
            now = datetime.datetime.now()
            hour = int(now.hour)
            minute = int(now.minute)
    except Exception as e:
        print(f"Error while parsing time: {traceback.format_exc()}")
        return 0.0
    return float(f"{hour}.{minute}")

def prep_slider_message(agent_id, min_val: float, max_val: float):
    buttons = [{"label": min_val, "action": ""}, {"label": max_val, "action": ""}]
    slider_message = prep_outgoing_message(agent_id, json.dumps({"items": buttons, "type": "slider"}), "keyboard")
    return slider_message

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


class HomeState(State):
    state_name = "HomeSate"
    
    def __init__(self) -> None:
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
        
    async def run(self):
        await asyncio.sleep(3)
        try:
            def services_options():
                return["Give me a recommendation", "Recommend based on ingredients"]
            print("SENDING Options:")
            await self.send(prep_outgoing_message(self.agent.id, "Here are the services that I can provide:"))
            system_cultural_factors = services_options()
            keyboard_message = prep_keyboard_message(self.agent.id, [{"label": factor, "action": factor} for factor in system_cultural_factors])
            await self.send(keyboard_message)
            message = await self.receive(REPLY_TIMEOUT)
            print(f"received {message}")
            selection = {}
            if message is not None and message.body == system_cultural_factors[0]:
                print(f"move to {message}")
                selection["text"] =  message.body
                selection["index"] = 0
                self.set_next_state(AskAllergiesState.get_state_name())
            elif message is not None and message.body == system_cultural_factors[1]:
                selection["text"] =  message.body
                selection["index"] = 1
                self.set_next_state(AskAllergiesState.get_state_name())            
            elif message is not None and message.body == "HOME":
                self.set_next_state(HomeState.get_state_name())
                return
            else:
                print("Please choose an option from the list.")
                self.set_next_state(HomeState.get_state_name())
                return
            # Save user selection
            with open(CACHE_DIR / "interactive" / f"{self.agent.id}_reco_type.pkl", "wb") as fp:
                pickle.dump(selection, fp)
            return
        except:
            traceback.print_exc()
            self.set_next_state("HomeState")
            
class CheckRecipeCompatibilityState(State):
    state_name = "checkRecipeCompatibilityState"
    
    def __init__(self):
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
        
    async def run(self):
        await asyncio.sleep(3)
        try:
            food_dataset = pd.read_csv("./modules/nvcbot/data/df_recipes.csv", index_col=0, sep="|")
            print("Query by ingredients...")
            # get user_features and transform it into  data frame 
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
                'meal_type_x': user_dict.get("meal_type_x", "lunch"),
                'time_of_meal_consumption': user_dict.get("time_of_meal_consumption", 12.0), 
                'place_of_meal_consumption': user_dict.get("place_of_meal_consumption", "restaurant"), 
                'social_situation_of_meal_consumption': user_dict.get("social_situation_of_meal_consumption", "alone")
            }
            # get ingredient list from the user 
            await self.send(prep_outgoing_message(self.agent.id, "Please write the ingredients separated by commas:"))
            message = await self.receive(REPLY_TIMEOUT)
            ingredients = ""
            if message is not None and message.body != "HOME":
                ingredients = message.body
            elif message is not None and message.body == "HOME":
                self.set_next_state(HomeState.get_state_name())
                return
            # quey recipes in db and answer 
            print(f"received {message}")
            prepare_data = {
                "profile": user_data,
                "context": context_features,
                "ingredients": ingredients
            }
            print(f"send_data: %s" % prepare_data)
            url = "http://localhost:8500/recommendByProximity/"
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
            selected_recipes = selected_recipes.reset_index(drop=True)
            # get recommendation
            await self.send(prep_outgoing_message(self.agent.id, "Based on your profile, preferences, and context, here are some recipes for you."))
            print(f"System Recipes: {selected_recipes}")
            buttons = []
            for i, recipe in selected_recipes.iterrows():
                await self.send(prep_outgoing_message(self.agent.id, f"option:{i} - {recipe['name'].title()}"))
                buttons += [{"label": f"See option: {i}", "action": recipe['recipeId']}]
                buttons += [{"label": f"Explain option: {i}", "action": f"explain_{recipe['recipeId']}"}]
            buttons += [{"label": "Get more recommendations", "action": "more_recommendations"}]
            keyboard_message = prep_keyboard_message(self.agent.id, buttons)
            await self.send(keyboard_message)
            # wait for an answer
            while True:
                message = await self.receive(REPLY_TIMEOUT)
                print(f"Received message from user: {message}")
                if message is not None and message.body == "HOME":
                    self.set_next_state(HomeState.get_state_name())
                    return
                if message is not None and message.body == "more_recommendations":
                    self.set_next_state(AskRecommendationsState.get_state_name())
                    print("next more recommendations")
                    return 
                elif message is not None and message.body in [f"explain_{recipe['recipeId']}" for i, recipe in selected_recipes.iterrows()]:
                    self.set_next_state(DisplayExplanationState.get_state_name())
                    print(f"next state explanation")
                    with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "wb") as fp:
                        pickle.dump(message.body, fp)
                    return
                elif message.body in [recipe['recipeId'] for i, recipe in selected_recipes.iterrows()]:
                    self.set_next_state(DisplayRecipeState.get_state_name())
                    print(f"next state detail")
                    with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "wb") as fp:
                        pickle.dump(message.body, fp)
                    return
        except:
            await self.send(prep_outgoing_message(self.agent.id, "Something went wrong let's try again."))
            self.set_next_state(HomeState.get_state_name())
            print(traceback.print_exc())
            
class GetFreeTextRecommendation(State):
    state_name = "GetFreeTextRecommendation"
    
    def __init__(self):
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
        
    async def run(self):
        await asyncio.sleep(3)
        try:
            print("SENDING FreeTextRecommendation")
            await self.send(prep_outgoing_message(self.agent.id, "Please provide recipe details:"))
            message = await self.receive(REPLY_TIMEOUT)
            if message is not None and message.body == "HOME":
                self.set_next_state(HomeState.get_state_name())
                return
            #TODO: preprocess text to send to back end.
            print(f"received {message}")
            await self.send(prep_outgoing_message(self.agent.id, "This function will be available soon."))
            self.set_next_state(HomeState.get_state_name())
        except:
            traceback.print_exc()
            self.set_next_state(HomeState.get_state_name())



# Define the state machine behaviour
class AskAllergiesState(State):
    
    state_name = "askAllergiesState"
    def __init__(self) -> None:
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
        
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
    
    state_name = "askCulturalFactorState"
    def __init__(self) -> None:
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
        
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
                self.set_next_state(AskFlexiObservantState.get_state_name())
            else:
                self.set_next_state(AskMealTypeState.get_state_name())

        except:
            traceback.print_exc()

class AskFlexiObservantState(State):
    
    state_name = "askFlexiObservantState"
    def __init__(self) -> None:
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
        
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
            self.set_next_state(AskMealTypeState.get_state_name())

        except:
            traceback.print_exc()
            
# context states 
class AskMealTypeState(State):
    
    state_name = "askMealTypeState"
    def __init__(self) -> None:
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
        
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
                user_dict["meal_type_x"] = meal_type[0]
            else:
                user_dict["meal_type_x"] = "lunch"

            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'wb') as file:
                pickle.dump(user_dict, file)
            self.set_next_state(AskPlaceState.get_state_name())
        except:
            traceback.print_exc()
            
class AskPlaceState(State):
    
    state_name = "askPlaceState"
    def __init__(self) -> None:
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
        
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
            self.set_next_state(AskSocialSituationState.get_state_name())
        except:
            traceback.print_exc()
            
class AskSocialSituationState(State):
    
    state_name = "askSocialSituationState"
    def __init__(self) -> None:
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
        
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
    
    state_name = "askTimeState"
    def __init__(self) -> None:
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
        
    async def run(self) -> None:
        await asyncio.sleep(3)
        
        try:
            print("SENDING TIME")
            await self.send(prep_outgoing_message(self.agent.id, "What time are you going to eat?"))
            system_times = get_time_options()
            keyboard_message = prep_keyboard_message(self.agent.id, [{"label": time.title(), "action": system_times[time]} for time in 
            system_times.keys()])
            
            await self.send(keyboard_message)
            meal_time = 0.0
            time_option = []
            message = await self.receive(REPLY_TIMEOUT)
            # process message 
            if message is not None and message.body.startswith('time:'):
                meal_time_str = message.body
                meal_time = get_time_from_text(meal_time_str)
                print(f"Captured meal time from front: {meal_time}")
            elif message is not None and message.body == system_times['other time']:
                meal_time = await self.send(prep_outgoing_message(self.agent.id, "Please enter the hour with this format (Hour:minute am/pm)."))
                message = await self.receive(REPLY_TIMEOUT)
                text = message.body
                text = text.lower()
                meal_time = get_time_from_text(text)
                if "pm" in text:
                    meal_time += 12
                print(f"Obtained time from user: {meal_time}")
            else:
                print(f"Option not valid or empty string")
            print("Meal time: ", meal_time)
            # load user profile and data 
            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)
            # save current date time to use in the recommendation
            user_dict['time_of_meal_consumption'] = meal_time
            # save the current state
            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'wb') as file:
                pickle.dump(user_dict, file)
                
            # load user selection and use it to choose 
            selection = None
            path = CACHE_DIR / "interactive" / f"{self.agent.id}_reco_type.pkl"
            if os.path.exists(path):
                print("Path selection exits, loading...")
                with open(path, "rb") as fp:
                    selection = pickle.load(fp)
                if selection is not None:
                    if selection["index"] == 0:
                        self.set_next_state(AskRecommendationsState.get_state_name())
                    else:
                        self.set_next_state(CheckRecipeCompatibilityState.get_state_name())
                    return
                else:
                    self.set_next_state(AskRecommendationsState.get_state_name())
            else:
                # default selection
                self.set_next_state(AskRecommendationsState.get_state_name())
        except:
            print(traceback.print_exc())
            await self.send(prep_outgoing_message(self.agent.id, "Something went wrong less try again."))
            self.set_next_state(HomeState.get_state_name())
            return
            
class AskTextQueryInsideDatabase(State):
    state_name = 'askTextQueryInsideDatabase'
    def __init__(self) -> None:
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
    
    async def run(self) -> None:
        await asyncio.sleep(3)
        
        try:
            #TODO: implement this state and join into the main structure
            print("SENDING TEXT QUERY")
            with open(USER_PROFILES_DIR /  f'{self.agent.id}.pkl', 'rb') as file:
                user_dict = pickle.load(file)
            if user_dict is not None:
                meal_time = user_dict.get('time_of_meal_consumption')
                place = user_dict.get('place_of_meal_consumption')
                social = user_dict.get('social_situation_of_meal_consumption')
                print(f"meal_time: {meal_time}, place: {place}, social: {social}")
        except Exception as e:
            traceback.print_exc()
            await self.send(prep_outgoing_message(self.agent.id, "Something went wrong less try again."))
            self.set_next_state(HomeState.get_state_name())
            return
        
class AskRecommendationWithOpenText(State):
    
    state_name = "askRecommendationWithOpenText"
    def __init__(self) -> None:
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
    
    async def run(self) -> None:
        await asyncio.sleep(3)
        
        try:
            print("SENDING RECOMMENDATIONS")
            #TODO: Implement open recommendations
            pass
        except Exception as e:
            traceback.print_exc()
            await self.send(prep_outgoing_message(self.agent.id, "Something went wrong less try again."))
            self.set_next_state(HomeState.get_state_name())
            return
            
class AskRecommendationsState(State):
    
    state_name = "askRecommendationsState"
    def __init__(self) -> None:
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
        
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
                'meal_type_x': user_dict.get("meal_type_x", "lunch"),
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
            selected_recipes = selected_recipes.reset_index(drop=True)
            # get recommendation
            await self.send(prep_outgoing_message(self.agent.id, "Based on your profile, preferences, and context, here are some recipes for you."))
            print(f"System Recipes: {selected_recipes}")
            buttons = []
            for i, recipe in selected_recipes.iterrows():
                await self.send(prep_outgoing_message(self.agent.id, f"option:{i} - {recipe['name'].title()}"))
                buttons += [{"label": f"See option: {i}", "action": recipe['recipeId']}]
                buttons += [{"label": f"Explain option: {i}", "action": f"explain_{recipe['recipeId']}"}]
            buttons += [{"label": "Get more recommendations", "action": "more_recommendations"}]
            keyboard_message = prep_keyboard_message(self.agent.id, buttons)
            await self.send(keyboard_message)
            print("Waiting for user answer...")
            message = await self.receive(REPLY_TIMEOUT)
            print(f"Received message {message}")
            while True:
                message = await self.receive(REPLY_TIMEOUT)
                if message.body == "more_recommendations":
                    self.set_next_state(AskRecommendationsState.get_state_name())
                    print("next more recommendations")
                    break
                elif message.body in [f"explain_{recipe['recipeId']}" for i, recipe in selected_recipes.iterrows()]:
                    self.set_next_state(DisplayExplanationState.get_state_name())
                    print(f"next state explanation")
                    with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "wb") as fp:
                        pickle.dump(message.body, fp)
                    break
                elif message.body in [recipe['recipeId'] for i, recipe in selected_recipes.iterrows()]:
                    self.set_next_state(DisplayRecipeState.get_state_name())
                    print(f"next state detail")
                    with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "wb") as fp:
                        pickle.dump(message.body, fp)
                    break
        except:
            traceback.print_exc()
            await self.send(prep_outgoing_message(self.agent.id, "Something went wrong less try again."))
            self.set_next_state(HomeState.get_state_name())
            return

class DisplayRecipeState(State):
    
    state_name = "displayRecipeInfoState"
    def __init__(self) -> None:
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
    
    async def run(self) -> None:
        # show recipe info 
        await asyncio.sleep(3)
        try:
            print(f"SHOW RECIPE")
            # load recipes 
            food_dataset = pd.read_csv("./modules/nvcbot/data/df_recipes.csv", index_col=0, sep="|")
            # load answer 
            with open(CACHE_DIR / "interactive" / f"{self.agent.id}.pkl", "rb") as fp:
                answer = pickle.load(fp)
            # load chosen selection 
            with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "rb") as fp:
                selected = pickle.load(fp)
            selected_recipe = food_dataset[food_dataset["recipeId"] == selected]
            selected_recipe.reset_index(drop=True, inplace=True)
            selected_recipe = selected_recipe.iloc[0].to_dict()
            print(f"Recipe: {selected_recipe}")
            
            msg = f"Title: {selected_recipe['name']}"
            await self.send(prep_outgoing_message(self.agent.id,
                                            msg
                                            ))
            msg = f"Ingredients: {selected_recipe['ingredients']}"
            await self.send(prep_outgoing_message(self.agent.id,
                                            msg
                                            ))
            msg = f"Instructions: {selected_recipe['instructions']}"
            await self.send(prep_outgoing_message(self.agent.id,
                                            msg
                                            ))
            msg = f"Calories: {selected_recipe['calories']}\nFiber: {selected_recipe['fiber']}\n"
            msg += f"Carbohydrates: {selected_recipe['carbohydrates']}\nFat: {selected_recipe['fat']}\n"
            msg += f"Taste profile: {selected_recipe['taste']}\nPrice: {int(selected_recipe['price'])*'$'}"
            print(f"Message to send: {msg}")
            await self.send(prep_outgoing_message(self.agent.id,
                                            msg
                                            ))
            await self.send(prep_outgoing_message(self.agent.id, get_google_image(selected_recipe['name']), body_format="image"))
            buttons = [{"label": "Accept recipe", "action": "accept"}, {"label": "Reject recipe", "action": "reject"},
                       {"label": "See Explanation", "action": "explain"}]
            keyboard_message = prep_keyboard_message(self.agent.id, buttons)
            await self.send(keyboard_message)
            message = await self.receive(REPLY_TIMEOUT)
            if message is not None and message.body == "HOME":
                self.set_next_state(HomeState.get_state_name())
                return
            elif message is not None and message.body == "accept":
                # Save accept feedback
                with open(CACHE_DIR / "interactive" / f"{self.agent.id}_pre_feed.pkl", "wb") as fp:
                    pickle.dump({"feed_type": "recipe", "id": selected, "status": "accept"}, fp)
                self.set_next_state(AskFeedBack.get_state_name())
                return 
            elif message is not None and message.body == "reject":
                # Save reject
                with open(CACHE_DIR / "interactive" / f"{self.agent.id}_pre_feed.pkl", "wb") as fp:
                    pickle.dump({"feed_type": "recipe", "id": selected, "status": "reject"}, fp)
                self.set_next_state(AskFeedBack.get_state_name())
                return 
            elif message is not None and message.body == "explain":
                self.set_next_state(DisplayExplanationState.get_state_name())
                return
            elif message.body == "BACK":
                self.set_next_state("askRecommendedState")
                with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "wb") as fp:
                    pickle.dump(message.body, fp)
                return 
            self.set_next_state(FinalState.get_state_name())
        except:
            print(traceback.format_exc())
            self.set_next_state(HomeState.get_state_name())

#TODO: Save user feedback in sql database
class DisplayExplanationState(State):
    
    state_name = "displayExplanationState"
    def __init__(self) -> None:
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
        
    async def run(self) -> None:
        try:
            # load answer 
            print(f"EXPLAIN RECIPE")
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
            await self.send(prep_outgoing_message(self.agent.id, "The following explanation is provided for your selected recipe"))
            await self.send(prep_outgoing_message(self.agent.id, answer["general_explanation"][i]))   
            await self.send(prep_outgoing_message(self.agent.id, "Would you like a detailed explanation please choose one form"))
            buttons = [{"label": "Rule Based", "action": "rule"},
                       {"label": "Probabilistic", "action": "probabilistic"},
                       {"label": "Give Feedback", "action": "feedback"},
                       {"label": "Leave", "action": "leave"}]
            keyboard_message = prep_keyboard_message(self.agent.id, buttons)
            await self.send(keyboard_message)
            message = await self.receive(REPLY_TIMEOUT)
            
            while message.body != "NONE" or message.body != "CONTINUE":
                print(f"Received message: {message.body}")
                if message.body == "feedback":
                    with open(CACHE_DIR / "interactive" / f"{self.agent.id}_pre_feed.pkl", "wb") as fp:
                        pickle.dump({"feed_type": "xai", "id": selected}, fp)
                    self.set_next_state(AskFeedBack.get_state_name())
                    print(f"Next state: Feedback")
                    break 
                elif message.body == "leave":
                    self.set_next_state(FinalState.get_state_name())
                    print("Next state Final")
                    break
                elif message.body == "BACK":
                    self.set_next_state(AskRecommendationsState.get_state_name())
                    with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "wb") as fp:
                        pickle.dump(message.body, fp)
                    break 
                elif message is not None and message.body == "HOME":
                    self.set_next_state(HomeState.get_state_name())
                    break
                elif message.body == "rule":
                    expa = answer["rule_based_explanation"][index]
                    await self.send(prep_outgoing_message(self.agent.id, expa))
                    with open(CACHE_DIR / "interactive" / f"{self.agent.id}_pre_feed.pkl", "wb") as fp:
                        pickle.dump({"feed_type": "xai", "id": selected, "xai_text": expa}, fp)
                    self.set_next_state(AskFeedBack.get_state_name())
                    break
                elif message.body == "probabilistic":
                    expa = answer["probabilistic_explanation"][index]
                    await self.send(prep_outgoing_message(self.agent.id, expa))
                    with open(CACHE_DIR / "interactive" / f"{self.agent.id}_pre_feed.pkl", "wb") as fp:
                        pickle.dump({"feed_type": "xai", "id": selected, "xai_text": expa}, fp)
                    self.set_next_state(AskFeedBack.get_state_name())
                    break
                elif message.body == "HOME":
                    self.set_next_state(HomeState.get_state_name())
                    break
                print("ENd of the state")
                message = await self.receive(REPLY_TIMEOUT)
            print("Outside of the state.")
        except:
            traceback.format_exc()
            self.set_next_state(HomeState.get_state_name())
            
class AskFeedBack(State):
    
    state_name = "askFeedbackState"
    def __init__(self) -> None:
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
    
    async def run(self) -> None:
        await asyncio.sleep(3)
        try:
            print("SENDING FEEDBACK")
            with open(CACHE_DIR / "interactive" / f"{self.agent.id}_state.pkl", "rb") as fp:
                selected = pickle.load(fp)
            print(selected)
            with open(CACHE_DIR / "interactive" / f"{self.agent.id}_pre_feed.pkl", "rb") as fp:
                feedback_data = pickle.load(fp)
            type = "recipe"
            if feedback_data["feed_type"] == "recipe":
                await self.send(prep_outgoing_message(self.agent.id, "Please choose in the scale how much did you liked the recipe."))
                slider_message = prep_slider_message(self.agent.id,
                                                     min_val=0.0, max_val=100.0)
                await self.send(slider_message)
            else:
                await self.send(prep_outgoing_message(self.agent.id, "Did you like the explanation recommended?"))
                type = "xai"
                buttons = [{"label": "Yes", "action": "yes"},
                       {"label": "No", "action": "no"}]
                keyboard_message = prep_keyboard_message(self.agent.id, buttons)
                await self.send(keyboard_message)
            # receive the user feedback 
            feedback_message = await self.receive(REPLY_TIMEOUT)
            if feedback_message is not None and feedback_message.body == "yes":
                #TODO: positive feedback 
                pass
            elif feedback_message is not None and feedback_message.body == "no":
                #TODO: negative feedback
                pass
            # ask for free text feedback 
            await self.send(prep_outgoing_message(self.agent.id, "Please complement your feedback with a short explanation on your decision:"))
            message = await self.receive(REPLY_TIMEOUT)
            now_time = dt.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            feedback_data.update({"date": now_time,"type": type, "message": message.body, "recipe": selected, 
                                  "binary_feedback": feedback_data})
            if os.path.exists(CACHE_DIR / "interactive" / f"{self.agent.id}_feedback.pkl"):
                with open(CACHE_DIR / "interactive" / f"{self.agent.id}_feedback.pkl", "rb") as fp:
                    f_dict_list = pickle.load(fp)
            else:
                f_dict_list = []
            f_dict_list.append(feedback_data)
            with open(CACHE_DIR / "interactive" / f"{self.agent.id}_feedback.pkl", "wb") as fp:
                pickle.dump(f_dict_list, fp)
            self.set_next_state(FinalState.get_state_name())
            return
        except:
            traceback.format_exc()
            self.set_next_state(HomeState.get_state_name())
            
class FinalState(State):
    
    state_name = "finalState"
    def __init__(self):
        super().__init__()
        
    @classmethod
    def get_state_name(cls):
        return cls.state_name
        
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
        if reply is not None and reply.body == "YES":
            self.set_next_state(HomeState.get_state_name())
            return  
        else:
            self.set_next_state(FinalState.get_state_name())
            return  





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