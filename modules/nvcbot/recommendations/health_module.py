import pandas as pd
import pathlib

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

def create_health_rating_scores(user_profile):
    nutritional_values = pd.read_pickle(pathlib.Path(__file__).parent / "data" / "diyetkolik_calories.pkl")

    user_based_score_df = pd.DataFrame()
    user_based_score_df.index = nutritional_values.index

    health_module = HealthModule(user_profile)
    health_module.calculate_scores(nutritional_values, user_based_score_df)

    user_based_score_df.dropna(inplace=True)

    user_based_score_df['overall'] = (
        1 * user_based_score_df['amr_score'] + 
        1 * user_based_score_df['health_score']) / 2
    user_based_score_df.sort_values(
        by=['overall'], inplace=True, ascending=False)

    return health_module.user_amr, user_based_score_df[["amr_score", "health_score", "overall"]]

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
        self.cv = 0.2

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

        print("amr stuff: ", self.user_bmr, activity_factor[self.user_exercice], user_daily_amr, meal_type_percentage[self.meal_type], user_recipe_amr)

        return user_recipe_amr

    def rate_nutrients(user_type, nutrient_type):
        if user_type == 'healthy':
            if nutrient_type == 'carbohydrates':
                rate = {
                    'min_rate': .45,
                    'average': .5,
                    'max_rate': .65,
                }
            elif nutrient_type == 'proteins':
                rate = {
                    'min_rate': .1,
                    'average': .2,
                    'max_rate': .35,
                }
            elif nutrient_type == 'fats':
                rate = {
                    'min_rate': .2,
                    'average': .3,
                    'max_rate': .35,
                }
            else:
                rate = 'Unknown'

        elif user_type == 'diabetic':
            if nutrient_type == 'cholesterol':
                rate = {
                    'max_rate': 200,
                }
            elif nutrient_type == ' saturated fats':
                rate = {
                    'max_rate': .07,
                }
            else:
                rate = 'Unknown'

        elif user_type == 'hypersensitive':
            if nutrient_type == 'sodium':
                rate = {
                    'max_rate': 2500,
                }
            else:
                rate = 'Unknown'

        elif user_type == 'overweight':
            if nutrient_type == 'saturated fats':
                rate = {
                    'max_rate': .1,
                }

            elif nutrient_type == 'proteins':
                rate = {
                    'average': .1,
                }

        else:
            rate = 'Unknown'
        return rate

    def calculate_scores(self, recipe_df: pd.DataFrame) -> pd.DataFrame:
        user_based_score_df = pd.DataFrame()

        user_based_score_df.index = recipe_df.index

        bins = [-1, (1 - self.cv) * self.user_amr, self.user_amr,
                (1 + self.cv) * self.user_amr]
        
        user_based_score_df['amr_score'] = pd.cut(
            recipe_df['calories'], bins=bins, labels=[1, 3, 5])
        user_based_score_df['amr_score'] = user_based_score_df['amr_score'].astype(
            float)

        protein_rate = {'min_rate': .1,
                        'average': .2,
                        'max_rate': .35,
                        }
        protein_multiplier = 4
        protein_score_masking = (self.user_amr * protein_rate['min_rate'] <= recipe_df['protein'] * protein_multiplier) &  \
                                (recipe_df['protein'] * protein_multiplier <=
                                 self.user_amr * protein_rate['max_rate'])
        user_based_score_df['protein_score'] = protein_score_masking.map({
                                                                         True: 5, False: 1})

        fat_rate = {'min_rate': .2,
                    'average': .3,
                    'max_rate': .35,
                    }
        fat_multiplier = 9
        fat_score_masking = (self.user_amr * fat_rate['min_rate'] <= recipe_df['fat'] * fat_multiplier) &  \
                            (recipe_df['fat'] * fat_multiplier <=
                             self.user_amr * fat_rate['max_rate'])
        user_based_score_df['fat_score'] = fat_score_masking.map(
            {True: 5, False: 1})

        carb_rate = {'min_rate': .45,
                     'average': .5,
                     'max_rate': .65,
                     }
        carb_multiplier = 4
        carb_score_masking = (self.user_amr * carb_rate['min_rate'] <= recipe_df['fat'] * carb_multiplier) &  \
                             (recipe_df['fat'] * carb_multiplier <=
                              self.user_amr * carb_rate['max_rate'])
        user_based_score_df['carb_score'] = carb_score_masking.map(
            {True: 5, False: 1})

        user_based_score_df['health_score'] = user_based_score_df[[
            "fat_score", "protein_score", "carb_score"]].mean(axis=1)
        
        return user_based_score_df[["fat_score", "protein_score", "carb_score", "amr_score", "health_score"]]
