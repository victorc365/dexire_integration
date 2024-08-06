from enum import Enum
import numpy as np
from typing import List, Dict, Any, Tuple
# Enumerators 
class Gender(str, Enum):
    """Enumeration to maintain clinical genders M for male and F for female.

    :param str: str class to save string constants representing the clinical gender.
    :type str: str
    :param Enum: Enumeration interface
    :type Enum: Enum
    """
    male = "M"
    female = "F"
    
class BMI_constants(str, Enum):
    """Enumeration to maintain the Body Index Mass (BMI) conditions:
    * underweight
    * healthy
    * overweight
    * obesity.

    :param str: str class to save string constants representing the BMI conditions.
    :type str: str
    :param Enum: Enumeration interface
    :type Enum: Enum
    """
    underweight = "underweight"
    healthy = "healthy"
    overweight = "overweight"
    obesity = "obesity"

class NutritionGoals(str, Enum):
    """Enumeration to maintain the nutrition goals:
    * lose_weight
    * maintain_fit
    * gain_weight.

    :param str: str class to save string constants representing the nutrition goals.
    :type str: str
    :param Enum: Enumeration interface
    :type Enum: Enum
    """
    lose_weight = "lose_weight"
    maintain_fit = "maintain_fit"
    gain_weight = "gain_weight"
    
class NutritionGoals(str, Enum):
    """Enumeration to maintain the nutrition goals:
    * lose_weight
    * maintain_fit
    * gain_weight.

    :param str: str class to save string constants representing the nutrition goals.
    :type str: str
    :param Enum: Enumeration interface
    :type Enum: Enum
    """
    lose_weight = "lose_weight"
    maintain_fit = "maintain_fit"
    gain_weight = "gain_weight"

class ActivityLevel(str, Enum):
    """Enumeration to maintain the activity levels:
    * Sedentary
    * Lightly active
    * Moderately active
    * Very active.

    :param str: str class to save string constants representing the activity level.
    :type str: str
    :param Enum: Enumeration interface
    :type Enum: Enum
    """
    sedentary = "Sedentary"
    light_active = "Lightly active"
    moderate_active = "Moderately active"
    very_active = "Very active"
    
def format_gender(gender_str: str) -> Gender:
    gender = gender_str.lower()
    if gender == "male" or gender == "m":
        return Gender.male.value
    else:
        return Gender.female.value
def format_activity_level(activity_level_str: str) -> ActivityLevel:
    activity_level = activity_level_str.lower()
    if activity_level == "sedentary":
        return ActivityLevel.sedentary.value
    elif activity_level == "lightly active":
        return ActivityLevel.light_active.value
    elif activity_level == "moderately active":
        return ActivityLevel.moderate_active.value
    elif activity_level == "very active":
        return ActivityLevel.very_active.value
    else:
        return str(ActivityLevel.sedentary)
def format_working_status(working_status_str: str) -> str:
    ws = working_status_str.lower()
    if ws == "employed":
        return "Full-time-worker"
    elif ws == "unemployed":
        return "Unemployed"
    elif ws == "retired":
        return "Unemployed"
    elif ws == "student":
        return "Unemployed"

def format_marital_status(marital_status_str: str) -> str:
    ms = marital_status_str.lower()
    if ms == "single":
        return "Single"
    elif ms == "married":
        return "Married"
    elif ms == "divorced":
        return "Single"
    elif ms == "widowed":
        return "Single"
def format_nutritional_goal(nutrition_goal_str: str) -> str:
    if nutrition_goal_str.lower() == "lose_weight":
        return NutritionGoals.lose_weight.value
    elif nutrition_goal_str.lower() == "maintain_fit":
        return NutritionGoals.maintain_fit.value
    elif nutrition_goal_str.lower() == "gain_weight":
        return NutritionGoals.gain_weight.value
        
class UserProfile:
    def __init__(self, user_data_dict: Dict[str, Any]) -> None:
        self.user_name = user_data_dict.get("user_name", "User")
        self.gender = format_gender(user_data_dict.get("gender", Gender.male.value))
        self.age = user_data_dict.get("age", 25)
        self.weight = user_data_dict.get("weight", 70)
        self.height = user_data_dict.get("height", 175)
        self.working_status = format_working_status(user_data_dict.get("working_status", "Unemployed"))
        self.marital_status = format_marital_status(user_data_dict.get("marital_status", "Single"))
        self.ethnicity = user_data_dict.get("ethnicity", "White")
        self.life_style = format_activity_level(user_data_dict.get("life_style", "Sedentary"))
        self.nutrition_goal = format_nutritional_goal(user_data_dict.get("nutrition_goal", NutritionGoals.maintain_fit.value))
        self.current_daily_calories = user_data_dict.get("current_daily_calories", 0.0)
        self.projected_daily_calories = user_data_dict.get("projected_daily_calories", 0.0)
        self.current_bmi = user_data_dict.get("current_bmi", BMI_constants.healthy.value)
        self.next_bmi = user_data_dict.get("next_bmi", BMI_constants.healthy.value)
        self.cultural_diet = user_data_dict.get("cultural_diet", "NotRestriction")
        self.allergies = user_data_dict.get("allergies", "NotAllergy")
        self.numeric_bmi = user_data_dict.get("numeric_bmi", 0.0)
        self.bmr = user_data_dict.get("bmr", 0.0)
        
    def calculate_bmi(self) -> Tuple[float, BMI_constants]:
        self.numeric_bmi = self.weight / ((self.height / 100) ** 2)
        if self.numeric_bmi < 18.5:
            self.current_bmi = BMI_constants.underweight
        elif self.numeric_bmi < 25:
            self.current_bmi = BMI_constants.healthy
        elif self.numeric_bmi < 30:
            self.current_bmi = BMI_constants.overweight
        elif self.numeric_bmi >= 30:
            self.current_bmi = BMI_constants.obesity
        return (self.numeric_bmi, self.current_bmi)
    
    def basal_metabolic_rate(self) -> float:
        BMR = 0
        if self.gender == Gender.male:
            # Numbers here are part of the Basal metabolic rate (BMR) formula.
            BMR = 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)
        else:
            BMR = 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * self.age)
        self.bmr = BMR
        return BMR
    
    def calculate_daily_calorie_needs(self, BMR: float, activity_level: ActivityLevel) -> float:
        """Calculate the daily calorie needs given the BMR and the activity level.

        :param BMR: Basal Metabolic Rate (BMR)
        :type BMR: float
        :param activity_level: user's activity level (e.g., sedentary, light active, moderate active)
        :type activity_level: ActivityLevel
        :return: Daily calorie needs
        :rtype: float
        """
        calories_daily = 1200 # minimum daily calorie requirement
        if activity_level == ActivityLevel.sedentary:
            calories_daily = 1.2 * BMR
        elif activity_level == ActivityLevel.light_active:
            calories_daily = 1.375 * BMR
        elif activity_level == ActivityLevel.moderate_active:
            calories_daily = 1.725 * BMR
        else:
            calories_daily = 1.9 * BMR
        self.current_daily_calories = calories_daily
        return np.max([calories_daily, 1200])
    
    def projected_calorie_needs(self) -> float:
        """Calculate the projected daily calorie needs given the activity level.
        :param activity_level: user's activity level (e.g., sedentary, light active, moderate active)
        :type activity_level: ActivityLevel
        :return: Projected daily calorie needs
        :rtype: float
        """
        projected_calories_need = 1200
        if self.nutrition_goal == NutritionGoals.gain_weight:
            # Add or remove calories to create metabolic deficit
            projected_calories_need = self.current_daily_calories + 500
        elif self.nutrition_goal == NutritionGoals.maintain_fit:
            projected_calories_need = self.current_daily_calories
        else:
            projected_calories_need = self.current_daily_calories - 500
        return np.max(np.array([projected_calories_need, 1200]))
    
    
    
        
        
        
    
    
    