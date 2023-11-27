import pandas as pd
import numpy as np
import os
import ast

class UserRatingModule:
    def __init__(self):
        user_rating_df_train = pd.read_csv("./datasets/archive/core-data-train_rating.csv")
        user_rating_df_test = pd.read_csv("./datasets/archive/core-data-test_rating.csv") 
        self.user_rating_df = pd.concat((user_rating_df_train, user_rating_df_test))

    def store_users_rating(self, new_df_score):
        # rated recipe id on Internet
        unique_recipe_id = self.user_rating_df.recipe_id.unique()
        
        for i in new_df_score.index:
            # the mean of all the ratings on Internet
            mean_rating = (self.user_rating_df[self.user_rating_df.recipe_id == i]).rating.mean()
            new_df_score.loc[i, 'internet_rating_score'] = mean_rating
            
        return new_df_score   
        