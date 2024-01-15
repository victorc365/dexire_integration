import pandas as pd
from modules.nvcbot.recommendations.health_module import create_health_rating_scores
from modules.nvcbot.recommendations.preferences_module import create_user_recipes

from modules.nvcbot import DATASETS_DIR, CACHE_DIR

import ast

import pickle

def generate_custom_recipes(uid, user_profile, user_health_scores, interaction):
    custom_recipes = create_user_recipes([user_profile["habits"]])

    nutritional_values: pd.DataFrame = pd.read_pickle(DATASETS_DIR / "diyetkolik_calories.pkl")
    user_health_scores: pd.DataFrame = pd.DataFrame.from_dict(ast.literal_eval(user_health_scores["healthscores"]))
    print(user_health_scores)

    merged_profile = custom_recipes.merge(
        nutritional_values, right_index=True, left_index=True)
    merged_profile = merged_profile.merge(
        user_health_scores, left_index=True, right_index=True).dropna()
    
    ## Normalize the overall health score.
    merged_profile["overall"] = merged_profile.health_score.transform(lambda row: row / row.max(), axis=0)
    merged_profile.sort_values(by=["overall"], ascending=False, inplace=True)
    merged_profile.loc[merged_profile.tail(10).index, "recommended"] = 0
    merged_profile.loc[merged_profile.tail(10).index, "recommendation_tags"] = \
    merged_profile.loc[merged_profile.tail(10).index].recommendation_tags.apply(lambda x: x.union(set(["UNHEALTHY_RECIPE"]))) 
    merged_profile.to_pickle(CACHE_DIR / f"{interaction}" / f"{uid}.pkl")

