import pandas as pd
import difflib

def compare_recipes(recipe_a, recipe_b):
    columns = [
                "final_matching_score",
                "overall",
                "carbohydrates",
                "protein",
                "fat",
                "calories",
                "fiber",
                ]
    
    ## "amr_score",
    ## "health_score",

    strong_points = [columns[idx] for idx, (a, b) in enumerate(zip(recipe_a[columns].tolist(), recipe_b[columns].tolist())) if a > b]
    weak_points = [column for column in columns if column not in strong_points]
    return strong_points, weak_points
    

def calculate_similarity_score(row, target):
    return difflib.SequenceMatcher(None, row, target).ratio()

def get_counter_explanation(recipes_df: pd.DataFrame, recommendation: pd.DataFrame):
    not_recommended: pd.DataFrame = recipes_df[recipes_df.recommended==0].head(5)
    best_worst_recipe_idx = not_recommended.Classes.apply(lambda row: calculate_similarity_score(row, recommendation.Classes)).idxmax()
    best_worst_recipe = not_recommended.loc[best_worst_recipe_idx]
    strong_points, weak_points = compare_recipes(recommendation, best_worst_recipe)[-2:]
    return strong_points, weak_points, best_worst_recipe
