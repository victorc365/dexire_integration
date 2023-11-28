import pandas as pd
import numpy as np

from modules.nvcbot.ontology import expand_classes
from modules.nvcbot import DATASETS_DIR, CACHE_DIR

def create_user_recipes(habits):
    habits = [habit for habit in habits if habit != "No Restrictions"]
    if not habits:
        custom_recipes: pd.DataFrame = pd.read_pickle(DATASETS_DIR / "archive" / "diyetkolik_with_classes.pkl")
    else:
        custom_recipes = pd.read_pickle(DATASETS_DIR / "habits" / f"diyetkolik_with_classes_{habits[0]}.pkl")
        for habit in habits[1:]:
            new_base = pd.read_pickle(DATASETS_DIR / "habits" / f"diyetkolik_with_classes_{habit}.pkl")
            both = pd.merge(custom_recipes, new_base, how='inner', right_index=True, left_index=True, suffixes=["", "_y"])
            both = both.drop([x for x in both.columns if "_y" in x], axis=1)

    custom_recipes.dropna(inplace=True)

    # 0: do not recommend
    # 1: can recommend
    # -1: has been recommended
    custom_recipes["recommended"] = 1
    custom_recipes["recommendation_tags"] = [set() for _ in range(custom_recipes.shape[0])]
    return custom_recipes


def process_cuisine_specs(uuid, interaction_type, wanted_cuisines, unwanted_cuisines):
    df = pd.read_pickle(CACHE_DIR / f"{interaction_type}" / f"{uuid}.pkl")
    unwanted_recipes = df[df.CuisineEnglish.isin(unwanted_cuisines)]
    df.loc[unwanted_recipes.index, "recommended"] = 0
    df.loc[unwanted_recipes.index, "recommendation_tags"] = df.loc[unwanted_recipes.index].recommendation_tags.apply(lambda x: x.union(set(["UNWANTED_CUISINE"]))) 

    df["cuisine_matching_score"] = df.Cuisine.apply(lambda row: 1 if row in wanted_cuisines else 0)
    df.to_pickle(f"./cache/{interaction_type}/{uuid}.pkl")

def process_ingredients_specs(uuid, interaction_type, wanted_ingredients, unwanted_ingredients):
    df = pd.read_pickle(CACHE_DIR / f"{interaction_type}" / f"{uuid}.pkl")

    unwanted_ingredients = expand_classes(unwanted_ingredients)
    wanted_ingredients = expand_classes(wanted_ingredients)

    print("expanded: ", unwanted_ingredients)

    for unwanted_ingr in unwanted_ingredients:
        unwanted_recipes = df.Classes.index[df.Classes.apply(lambda x: unwanted_ingr in x)]
        df.loc[unwanted_recipes, "recommended"] = 0
        df.loc[unwanted_recipes, "recommendation_tags"] = df.loc[unwanted_recipes].recommendation_tags.apply(lambda x: x.union(set(["UNWANTED_INGREDIENTS"]))) 

    df["ingredient_matching_score"] = df.Classes.apply(lambda row: len(np.intersect1d(row, wanted_ingredients)) / len(np.union1d(row, wanted_ingredients)))
    df["final_matching_score"] = df["cuisine_matching_score"] + df["ingredient_matching_score"]

    if df["final_matching_score"].max() != 0:
        df["final_matching_score"] = df["final_matching_score"].transform(lambda x: x / x.max(), axis=0)

    df["total_score"] = df["final_matching_score"] * 0.5 + df["overall"] * 0.5 
    df.sort_values("total_score", ascending=False, inplace=True)

    df.to_pickle(f"./cache/{interaction_type}/{uuid}.pkl")