import json
import traceback
import pickle
import pandas as pd
import typing as t
import requests
import datetime as dt
import re
import requests

from core.src.mas.agents.personal_agent.behaviours.contextual_fsm import AbstractContextualFSMBehaviour
from core.src.services.persistence_service import PryvPersistenceService

from modules.nvcbot.db.models import *
from modules.nvcbot import CACHE_DIR, USER_PROFILES_DIR
from bs4 import BeautifulSoup

from modules.nvcbot.recommendations.user_profile import UserProfile
from modules.nvcbot.states.nvc_states import (HomeState, AskAllergiesState, AskCulturalFactorState,
                                              AskMealTypeState, AskPlaceState,
                                              AskSocialSituationState, AskTimeState, AskRecommendationsState,
                                              DisplayExplanationState, DisplayRecipeState, AskFeedBack,
                                              FinalState, CheckRecipeCompatibilityState)

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
        self.add_state(name=CheckRecipeCompatibilityState.get_state_name(),
                       state=CheckRecipeCompatibilityState())
        
        # Add transitions
        self.add_transition(HomeState.get_state_name(), HomeState.get_state_name())
        self.add_transition(HomeState.get_state_name(), AskAllergiesState.get_state_name())
    
        self.add_transition(AskAllergiesState.get_state_name(), AskCulturalFactorState.get_state_name())
        self.add_transition(AskCulturalFactorState.get_state_name(), AskMealTypeState.get_state_name())
        self.add_transition(AskMealTypeState.get_state_name(), AskPlaceState.get_state_name())
        self.add_transition(AskPlaceState.get_state_name(), AskSocialSituationState.get_state_name())
        self.add_transition(AskSocialSituationState.get_state_name(), AskTimeState.get_state_name())
        self.add_transition(AskTimeState.get_state_name(), AskRecommendationsState.get_state_name())
        self.add_transition(AskTimeState.get_state_name(), CheckRecipeCompatibilityState.get_state_name())
        self.add_transition(AskRecommendationsState.get_state_name(), FinalState.get_state_name())
        self.add_transition(AskRecommendationsState.get_state_name(), AskRecommendationsState.get_state_name())
        self.add_transition(AskRecommendationsState.get_state_name(), DisplayRecipeState.get_state_name())
        self.add_transition(AskRecommendationsState.get_state_name(), DisplayExplanationState.get_state_name())
        self.add_transition(CheckRecipeCompatibilityState.get_state_name(), DisplayRecipeState.get_state_name())
        self.add_transition(CheckRecipeCompatibilityState.get_state_name(), DisplayExplanationState.get_state_name())
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
        self.add_transition(AskMealTypeState.get_state_name(), HomeState.get_state_name())
        self.add_transition(AskPlaceState.get_state_name(), HomeState.get_state_name())
        self.add_transition(AskSocialSituationState.get_state_name(), HomeState.get_state_name())
        self.add_transition(AskTimeState.get_state_name(), HomeState.get_state_name())
        self.add_transition(AskRecommendationsState.get_state_name(), HomeState.get_state_name())
        self.add_transition(CheckRecipeCompatibilityState.get_state_name(), HomeState.get_state_name())
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
        self.add_transition(AskMealTypeState.get_state_name(), AskCulturalFactorState.get_state_name())
        self.add_transition(AskPlaceState.get_state_name(), AskMealTypeState.get_state_name())
        self.add_transition(AskSocialSituationState.get_state_name(), AskPlaceState.get_state_name())
        self.add_transition(AskTimeState.get_state_name(), AskSocialSituationState.get_state_name())
        self.add_transition(AskRecommendationsState.get_state_name(), AskTimeState.get_state_name())
        self.add_transition(CheckRecipeCompatibilityState.get_state_name(), AskTimeState.get_state_name())
        self.add_transition(DisplayRecipeState.get_state_name(), AskRecommendationsState.get_state_name())
        self.add_transition(DisplayExplanationState.get_state_name(), AskRecommendationsState.get_state_name())
        self.add_transition(DisplayRecipeState.get_state_name(), CheckRecipeCompatibilityState.get_state_name())
        self.add_transition(DisplayExplanationState.get_state_name(), CheckRecipeCompatibilityState.get_state_name())
        self.add_transition(DisplayExplanationState.get_state_name(), DisplayRecipeState.get_state_name())
        self.add_transition(FinalState.get_state_name(), AskRecommendationsState.get_state_name())
        self.add_transition(FinalState.get_state_name(), HomeState.get_state_name())
        self.add_transition(FinalState.get_state_name(), AskRecommendationsState.get_state_name())
        self.add_transition(FinalState.get_state_name(), CheckRecipeCompatibilityState.get_state_name())


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

