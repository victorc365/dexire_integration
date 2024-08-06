import tensorflow as tf
import numpy as np
import pandas as pd

from typing import Dict

from tensorflow.keras.layers import (StringLookup,
                                     TextVectorization,
                                     Embedding,
                                     Normalization,
                                     Concatenate,
                                     Flatten,
                                     Dropout,
                                     GlobalAveragePooling1D)

# Mix with the embeddings
def get_embeddings_recipe_id(recipe_id: str, embedding_dict: Dict[str, np.array]):
  if recipe_id in embedding_dict.keys():
    return embedding_dict[recipe_id]
  else:
    return np.nan

# generate features dictionaries
def generate_features(df, feature_list, numeric_features):
  dict_features = {}
  for feature in feature_list:
    print(f"feature: {feature}")
    if feature in numeric_features:
      #print(f"feature numeric: {feature}")
      dict_features[feature] = tf.convert_to_tensor(df[feature].values, tf.float32, name=f"{feature}")
    else:
      print(f"dtype: {df[feature].dtype} feature:{feature}")
      dict_features[feature] = tf.convert_to_tensor(df[feature].values, tf.string, name=f"{feature}")
  return dict_features


def generate_dataset_from_pandas(df:pd.DataFrame, numeric_features, feature_columns, embedding_columns, target_col=None):
  dict_features = generate_features(df, feature_columns, numeric_features)
  dict_embeddings = {}
  for emb_col in embedding_columns:
    dict_embeddings[emb_col] = tf.convert_to_tensor(np.array(df.loc[:, emb_col].tolist()), dtype=tf.float32)
  dict_features.update(dict_embeddings)
  features = tf.data.Dataset.from_tensor_slices(dict_features)
  #dict_labels = generate_features(train, TARGET_FEATURE_LABELS, TARGET_FEATURE_LABELS)
  if target_col is not None:
    labels = tf.data.Dataset.from_tensor_slices(tf.convert_to_tensor(df.loc[:, target_col].values, dtype=tf.float32))
    # embeddings_ds = tf.data.Dataset.from_tensor_slices(dict_features)
    # features_ds = tf.data.Dataset.zip((features, embeddings_ds))
    ds = tf.data.Dataset.zip((features, labels))
    #train_ds = tf.data.Dataset.from_tensor_slices((features_list, labels_list))
    return ds
  else:
      return features

# fill nan in columns
def check_nans(df_test):
  dict_col_nans = {}
  for col in df_test.columns:
    dict_col_nans[col] = sum(df_test[col].isna())
  return dict_col_nans

def filter_recipes_by_embedding(df_data: pd.DataFrame, 
                                embedding_dict: Dict[str, np.array],
                                recipe_id_col: str = "recipeId"):
    mask_data = df_data[recipe_id_col].isin(list(embedding_dict.keys()))
    filtered_data =df_data.loc[mask_data, :]
    return filtered_data


# generate datasets from data
def identify_data_types(input_list):
  numeric_features = []
  categorical_features = []
  embedding_list = []
  for feat in input_list:
    size = feat.shape[-1]
    if size > 1:
      embedding_list.append(feat.name)
    else:
      if feat.dtype == tf.string:
        categorical_features.append(feat.name)
      else:
        numeric_features.append(feat.name)
  return numeric_features, categorical_features, embedding_list
