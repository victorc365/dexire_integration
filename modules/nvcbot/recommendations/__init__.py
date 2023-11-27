import pandas as pd
from application.recommendations.health_module import create_health_rating_scores
from application.recommendations.preferences_module import create_user_recipes
from application import DATASETS_DIR, CACHE_DIR

import pickle

def generate_custom_recipes(generated_uuid, user_profile, interaction):
    custom_recipes = create_user_recipes(user_profile["habits"])
    user_amr, user_health_score = create_health_rating_scores(user_profile)

    with open(CACHE_DIR / 'user_profiles' / f'{generated_uuid}.pkl', 'rb') as handle:
        user_profile = pickle.load(handle)
        user_profile["amr"] = user_amr

    with open(CACHE_DIR / 'user_profiles' / f'{generated_uuid}.pkl', 'wb') as handle:
        pickle.dump(user_profile, handle, protocol=pickle.HIGHEST_PROTOCOL)

    nutritional_values: pd.DataFrame = pd.read_pickle(DATASETS_DIR / "archive" / "diyetkolik_calories.pkl")

    merged_profile = custom_recipes.merge(
        nutritional_values, right_index=True, left_index=True)
    merged_profile = merged_profile.merge(
        user_health_score, left_index=True, right_index=True).dropna()
    
    ## Normalize the overall health score.
    merged_profile["overall"] = merged_profile.overall.transform(lambda row: row / row.max(), axis=0)
    merged_profile.sort_values(by=["overall"], ascending=False, inplace=True)
    merged_profile.loc[merged_profile.tail(10).index, "recommended"] = 0
    merged_profile.loc[merged_profile.tail(10).index, "recommendation_tags"] = \
    merged_profile.loc[merged_profile.tail(10).index].recommendation_tags.apply(lambda x: x.union(set(["UNHEALTHY_RECIPE"]))) 
    merged_profile.to_pickle(CACHE_DIR / f"{interaction}" / f"{generated_uuid}.pkl")

