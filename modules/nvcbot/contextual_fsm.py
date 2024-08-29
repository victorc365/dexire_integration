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
from modules.nvcbot.db.models import *
from modules.nvcbot import CACHE_DIR, USER_PROFILES_DIR
from bs4 import BeautifulSoup

from modules.nvcbot.recommendations.user_profile import UserProfile
from modules.nvcbot.states.nvc_states import (HomeState, AskAllergiesState, AskCulturalFactorState,
                                              AskFlexiObservantState, AskMealTypeState, AskPlaceState,
                                              AskSocialSituationState, AskTimeState, AskRecommendationsState,
                                              DisplayExplanationState, DisplayRecipeState, AskFeedBack,
                                              FinalState)


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

# Contextual fsm 
class ContextualFSM(AbstractContextualFSMBehaviour):
    def __init__(self):
        super().__init__()

    def setup(self):
        super().setup()
  
        # Add states 
        self.add_state(name=HomeState.get_state_name(),
                       state=HomeState(),
                       initial=True)
        self.add_state(name=AskAllergiesState.get_state_name(),
                       state=AskAllergiesState())
        self.add_state(name=AskCulturalFactorState.get_state_name(),
                       state=AskCulturalFactorState())
        self.add_state(name=AskFlexiObservantState.get_state_name(),
                       state=AskFlexiObservantState())
        # contextual state
        self.add_state(name=AskMealTypeState.get_state_name(),
                       state=AskMealTypeState())
        self.add_state(name=AskPlaceState.get_state_name(),
                       state=AskPlaceState())
        self.add_state(name=AskSocialSituationState.get_state_name(),
                       state=AskSocialSituationState())
        self.add_state(name=AskTimeState.get_state_name(),
                       state=AskTimeState())
        # Recommendation
        self.add_state(name=AskRecommendationsState.get_state_name(),
                       state=AskRecommendationsState())
        self.add_state(name=DisplayRecipeState.get_state_name(),
                       state=DisplayRecipeState())
        self.add_state(name=DisplayExplanationState.get_state_name(),
                       state=DisplayExplanationState())
        self.add_state(name=AskFeedBack.get_state_name(),
                       state=AskFeedBack())
        self.add_state(name=FinalState.get_state_name(),
                       state=FinalState())
        
        # Add transitions
        self.add_transition(HomeState.get_state_name(), HomeState.get_state_name())
        self.add_transition(HomeState.get_state_name(), AskAllergiesState.get_state_name())
    
        self.add_transition(AskAllergiesState.get_state_name(), AskCulturalFactorState.get_state_name())
        self.add_transition(AskCulturalFactorState.get_state_name(), AskFlexiObservantState.get_state_name())
        self.add_transition(AskCulturalFactorState.get_state_name(), AskMealTypeState.get_state_name())
        self.add_transition(AskFlexiObservantState.get_state_name(), AskMealTypeState.get_state_name())
        self.add_transition(AskMealTypeState.get_state_name(), AskPlaceState.get_state_name())
        self.add_transition(AskPlaceState.get_state_name(), AskSocialSituationState.get_state_name())
        self.add_transition(AskSocialSituationState.get_state_name(), AskTimeState.get_state_name())
        self.add_transition(AskTimeState.get_state_name(), AskRecommendationsState.get_state_name())
        self.add_transition(AskRecommendationsState.get_state_name(), FinalState.get_state_name())
        self.add_transition(AskRecommendationsState.get_state_name(), AskRecommendationsState.get_state_name())
        self.add_transition(AskRecommendationsState.get_state_name(), DisplayRecipeState.get_state_name())
        self.add_transition(AskRecommendationsState.get_state_name(), DisplayExplanationState.get_state_name())
        self.add_transition(DisplayRecipeState.get_state_name(), AskFeedBack.get_state_name())
        self.add_transition(DisplayExplanationState.get_state_name(), AskFeedBack.get_state_name())
        self.add_transition(DisplayRecipeState.get_state_name(), FinalState.get_state_name())
        self.add_transition(DisplayRecipeState.get_state_name(), DisplayExplanationState.get_state_name())
        self.add_transition(DisplayExplanationState.get_state_name(), FinalState.get_state_name())
        self.add_transition(AskFeedBack.get_state_name(), FinalState.get_state_name())
        self.add_transition(FinalState.get_state_name(), FinalState.get_state_name())
        self.add_transition(FinalState.get_state_name(), HomeState.get_state_name())
        
        # ADD transitions to home state from everybody
        self.add_transition(AskAllergiesState.get_state_name(), HomeState.get_state_name())
        self.add_transition(AskCulturalFactorState.get_state_name(), HomeState.get_state_name())
        self.add_transition(AskCulturalFactorState.get_state_name(), HomeState.get_state_name())
        self.add_transition(AskFlexiObservantState.get_state_name(), HomeState.get_state_name())
        self.add_transition(AskMealTypeState.get_state_name(), HomeState.get_state_name())
        self.add_transition(AskPlaceState.get_state_name(), HomeState.get_state_name())
        self.add_transition(AskSocialSituationState.get_state_name(), HomeState.get_state_name())
        self.add_transition(AskTimeState.get_state_name(), HomeState.get_state_name())
        self.add_transition(AskRecommendationsState.get_state_name(), HomeState.get_state_name())
        self.add_transition(FinalState.get_state_name(), FinalState.get_state_name())
        self.add_transition(FinalState.get_state_name(), HomeState.get_state_name())
        self.add_transition(DisplayRecipeState.get_state_name(), HomeState.get_state_name())
        self.add_transition(DisplayExplanationState.get_state_name(), HomeState.get_state_name())
        self.add_transition(DisplayRecipeState.get_state_name(), HomeState.get_state_name())
        self.add_transition(DisplayExplanationState.get_state_name(), HomeState.get_state_name())
        self.add_transition(AskFeedBack.get_state_name(), HomeState.get_state_name())
        
        # ADD BACK transitions
        self.add_transition(AskAllergiesState.get_state_name(), HomeState.get_state_name())
    
        self.add_transition(AskCulturalFactorState.get_state_name(), AskAllergiesState.get_state_name())
        self.add_transition(AskFlexiObservantState.get_state_name(), AskCulturalFactorState.get_state_name())
        self.add_transition(AskMealTypeState.get_state_name(), AskCulturalFactorState.get_state_name())
        self.add_transition(AskMealTypeState.get_state_name(), AskFlexiObservantState.get_state_name())
        self.add_transition(AskPlaceState.get_state_name(), AskMealTypeState.get_state_name())
        self.add_transition(AskSocialSituationState.get_state_name(), AskPlaceState.get_state_name())
        self.add_transition(AskTimeState.get_state_name(), AskSocialSituationState.get_state_name())
        self.add_transition(AskRecommendationsState.get_state_name(), AskTimeState.get_state_name())
        self.add_transition(FinalState.get_state_name(), AskRecommendationsState.get_state_name())
        self.add_transition(FinalState.get_state_name(), HomeState.get_state_name())


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

