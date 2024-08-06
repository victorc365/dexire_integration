import pandas as pd
import tensorflow as tf
import traceback
import numpy as np
from .model_utilities import (identify_data_types, 
                             generate_dataset_from_pandas, 
                             filter_recipes_by_embedding,
                             get_embeddings_recipe_id)

from functools import partial

class RecommenderService:
    def __init__(self, model_path: str):
        try:
            self.model = tf.keras.models.load_model(model_path)
            print("model loaded successfully.")
        except:
            traceback.print_exc()
            
    def load_embeddings(self, embeddings_path: str):
        try:
            # load embedding if it is necessary
            self.embeddings = dict(np.load(embeddings_path))
            print(f"Embedding loaded shape: {len(self.embeddings)}")
        except:
            traceback.print_exc()
    
    def recommended_recipes(self, 
                            df_data: pd.DataFrame, 
                            topk: int = 2, 
                            col_id_item: str = "recipeId", 
                            emb_col: str = "embeddings"):
        print("Started recommendation method...")
        try:
            if self.model is None or self.embeddings is None:
                print("Recommended recipes has started...")
                print(f"{df_data.shape}")
                df_filtered = filter_recipes_by_embedding(df_data, self.embeddings, col_id_item)
                # add embedding columns
                get_recipe_emb = partial(get_embeddings_recipe_id, embedding_dict=self.embeddings)
                df_filtered.loc[:, emb_col] = df_filtered[col_id_item].apply(lambda x: get_recipe_emb(x))
                list_candidates = df_filtered[col_id_item].tolist()
                model_inputs = self.model.inputs
                numeric_feat, categorical_feat, embed_feat = identify_data_types(model_inputs)
                pred_ds = generate_dataset_from_pandas(df_filtered,
                                            numeric_feat,
                                            feature_columns=numeric_feat+categorical_feat,
                                            embedding_columns=embed_feat,
                                            target_col=None)
                pred_ds = pred_ds.batch(32)
                predictions=self.model.predict(pred_ds)
                predictions_list = predictions.tolist()
                scored_candidates = list(zip(list_candidates, predictions_list))
                # order 
                return sorted(scored_candidates, key=lambda x: x[1], reverse=True)[:topk]
        except:
            traceback.print_exc()
            return []
