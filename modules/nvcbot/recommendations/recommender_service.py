import pandas as pd


class RecommenderService:
    def __init__(self, config_file: str):
        pass
    
    def recommended_recipes(self, recipe_sample: pd.DataFrame, topk: int = 2):
        recipes = recipe_sample.sample(n=topk)
        return recipes