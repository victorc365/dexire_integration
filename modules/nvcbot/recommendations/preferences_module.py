import pandas as pd
import numpy as np

from modules.nvcbot import DATASETS_DIR, CACHE_DIR


def create_user_recipes(habits):
    habits = [habit for habit in habits if habit != "None"]

    custom_recipes: pd.DataFrame = pd.read_csv(DATASETS_DIR / "df_final_7000_with_classes.csv", index_col=0)
    custom_recipes.dropna(inplace=True)

    if habits:
        custom_recipes = custom_recipes.loc[custom_recipes.cultural_restriction.isin(habits).index]

    custom_recipes["recommended"] = 0
    custom_recipes["recommendation_tags"] = [set() for _ in range(custom_recipes.shape[0])]
    return custom_recipes


def process_ingredients_specs(uuid, wanted_ingredients, unwanted_ingredients, interaction_type="interactive"):
    df: pd.DataFrame = pd.read_pickle(CACHE_DIR / f"{interaction_type}" / f"{uuid}.pkl")

    df.to_pickle(CACHE_DIR / f"{interaction_type}" / "before_ing_specs.pkl")
    
    print("------")
    print(wanted_ingredients)
    print(unwanted_ingredients)
    # unwanted_ingredients = expand_classes(unwanted_ingredients)
    # wanted_ingredients = expand_classes(wanted_ingredients)

    for unwanted_ingr in unwanted_ingredients:
        unwanted_recipes = df.ingredient_classes.index[df.ingredient_classes.apply(lambda x: unwanted_ingr in x)]
        df.loc[unwanted_recipes, "recommended"] = -1
        df.loc[unwanted_recipes, "recommendation_tags"] = df.loc[unwanted_recipes].recommendation_tags.apply(lambda x: x.union(set(["UNWANTED_INGREDIENTS"]))) 

    if wanted_ingredients is not None:
        df["ingredient_matching_score"] = df.ingredient_classes.apply(lambda row: len(np.intersect1d(row, wanted_ingredients)) / len(np.union1d(row, wanted_ingredients)))
        df["final_matching_score"] = df["ingredient_matching_score"] # df["cuisine_matching_score"] +

        if df["final_matching_score"].max() != 0:
            df["final_matching_score"] = df["final_matching_score"].transform(lambda x: x / x.max(), axis=0)

        df["total_score"] = df["final_matching_score"] * 0.5 + df["overall"] * 0.5 
        df.sort_values("total_score", ascending=False, inplace=True)

    df.to_pickle(CACHE_DIR / f"{interaction_type}" / f"{uuid}.pkl")