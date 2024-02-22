import pandas as pd
import pathlib
import math

def text_cleaning(cols):
    if cols == '< 1':
        return 1
    else:
        return cols

activity_factor = {
    'sedentary': 1.2,
    'lightly_active': 1.375,
    'moderately_active': 1.55,
    'active': 1.725,
    'very_active': 1.9,
}

meal_type_percentage = {
    'breakfast': .15,
    'lunch': .45,
    'dinner': .4
}

class HealthModule:
    def __init__(self, user_data):
        self.user_weight = user_data["weight"]
        self.user_height = user_data["height"]
        self.user_age = user_data["age"]
        self.user_sex = user_data["gender"]
        self.user_exercice = user_data["sports"]
        self.meal_type = user_data["mealtype"]
        self.user_bmr = 0
        self.user_amr = 0

    def bmr(self):
        if self.user_bmr != 0:
            return self.user_bmr
        if (self.user_sex.lower() == 'male'):
            user_bmr = 10*self.user_weight + 6.25*self.user_height - 5*self.user_age + 5
        else:
            user_bmr = 10*self.user_weight + 6.25*self.user_height - 5*self.user_age - 161

        self.user_bmr = user_bmr
        return user_bmr 

    def amr(self):
        if (self.user_amr != 0):
            return self.user_amr
        
        user_daily_amr = self.user_bmr * activity_factor[self.user_exercice]
        user_recipe_amr = user_daily_amr * meal_type_percentage[self.meal_type]

        self.user_amr = user_recipe_amr

        return user_recipe_amr

    def calculate_scores(self, recipe_df: pd.DataFrame, target_profile: dict) -> pd.DataFrame:
        self.bmr()
        self.amr()

        nutrient_cols = ["carbs","fat","fiber","protein"]

        nutrient_percentages = recipe_df[nutrient_cols].apply(lambda row: row / row.sum(), axis=1)
        nutrient_percentages["calorie_percentage"] = recipe_df["calories"] / self.amr()

        def get_distances(row):
            point1 = (target_profile[key] for key in nutrient_cols)
            point2 = (row[key] for key in nutrient_cols)

            point1 = (*point1, target_profile["calories"])
            point2 = (*point2, row["calorie_percentage"])

            return math.dist(point1, point2)

        nutrient_percentages["profile_distance"] = nutrient_percentages.apply(get_distances, axis=1)
        min_distance = nutrient_percentages["profile_distance"].min()
        max_distance = nutrient_percentages["profile_distance"].max()
        nutrient_percentages["health_score"] = nutrient_percentages["profile_distance"].apply(lambda d: (1 - (d - min_distance) / (max_distance - min_distance)))
        return nutrient_percentages