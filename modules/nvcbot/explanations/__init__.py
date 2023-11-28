import pandas as pd
import pickle
import ast

from modules.nvcbot import DATASETS_DIR, CACHE_DIR
from modules.nvcbot.explanations.item_user_based_explanations import TreeManager
from modules.nvcbot.explanations.sentence_generator import get_sentence, get_single_food_fact, get_counter_sentence
from modules.nvcbot.explanations.counter_explanations import get_counter_explanation

from database_models import *

def get_explanations(uuid, recommended_recipe):
    user_recipes: pd.DataFrame = pd.read_pickle(CACHE_DIR / "interactive" / f"{uuid}.pkl")

    user_recipes = user_recipes.replace("-", 0)

    #user_prefs = ast.literal_eval(list(IngredientSpecificationLogs.select().where(IngredientSpecificationLogs.uuid == uuid))[-1].user_data)['wanted_items']
    #cuisine_prefs = ast.literal_eval(list(CuisineSpecificationLogs.select().where(CuisineSpecificationLogs.uuid == uuid))[-1].user_data)['wanted_items']

    with open(CACHE_DIR / "user_profiles" / f"{uuid}.pkl", 'rb') as handle:
        user_profile = pickle.load(handle)  

    nutritional_cols = ["calories", "fat", "carbohydrates", "protein", "fiber"]
    recipe_cols = ["PrepTime", "CookingTime", "overall", "cuisine_matching_score", "ingredient_matching_score", "final_matching_score"]
    item_based_df = user_recipes[[*nutritional_cols, *recipe_cols, "recommended"]]

    item_based_tree = TreeManager(item_based_df)
    importances, indices, features = item_based_tree.get_features()
    
    explanations = []

    features.remove("overall")
    for feature in features[-3:]: #get the best 3 features
        content, expanded = get_single_food_fact(feature)
        explanations.append({
            "content": content, 
            "expanded": expanded,
            "effect": "positive",
        })

    #strong counter points is for the factors where recommended recipe is actually better than the counter recipe
    strong_counter_points, weak_counter_points, counter_recipe = get_counter_explanation(user_recipes, recommended_recipe)
    counter_explanation_sentence = get_counter_sentence(strong_counter_points[:2], weak_counter_points[2:], recommended_recipe, counter_recipe)

    explanations.append({
            "content": counter_explanation_sentence, 
            "expanded": None,
            "effect": "neutral",
        },)

    return explanations