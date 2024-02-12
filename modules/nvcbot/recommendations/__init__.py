import pandas as pd
from modules.nvcbot.recommendations.health_module import create_health_rating_scores
from modules.nvcbot.recommendations.preferences_module import create_user_recipes

from modules.nvcbot import DATASETS_DIR, CACHE_DIR, DATASET

import ast

def get_allergies():
    return ["gluten", "nuts", "dairy", "soy", "shellfish"]


def get_eating_habits():
    return ["vegan", "vegetarian", "kosher", "halal", "none"]


def get_recipe_classes():
    return ["beef", "pork", "poultry", "dairy", "seafood", "onion", "tomato", "mushroom"]
    

def generate_custom_recipes(uid, user_profile, user_health_scores, interaction):
    custom_recipes = create_user_recipes([user_profile["habits"]])

    user_health_scores: pd.DataFrame = pd.DataFrame.from_dict(user_health_scores["healthscores"])
    user_health_scores.index = user_health_scores.index.astype(int)

    merged_profile = custom_recipes.merge(
        user_health_scores, left_index=True, right_index=True).dropna()

    ## Normalize the overall health score.
    merged_profile["overall"] = merged_profile.health_score.transform(lambda row: row / row.max(), axis=0)
    merged_profile.sort_values(by=["overall"], ascending=False, inplace=True)
    one_thirds = merged_profile.shape[0] // 3
    merged_profile.loc[merged_profile.tail(one_thirds).index, "recommended"] = -1
    merged_profile.loc[merged_profile.tail(one_thirds).index, "recommendation_tags"] = \
    merged_profile.loc[merged_profile.tail(one_thirds).index].recommendation_tags.apply(lambda x: x.union(set(["UNHEALTHY_RECIPE"]))) 
    merged_profile.to_pickle(CACHE_DIR / f"{interaction}" / f"{uid}.pkl")

