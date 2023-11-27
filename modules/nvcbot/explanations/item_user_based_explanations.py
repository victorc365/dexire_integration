import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier

class TreeManager():
    def __init__(self, custom_recipes) -> None:
        self.X = custom_recipes.drop(['recommended'], axis=1)  
        self.y = custom_recipes['recommended']

        self.clf = DecisionTreeClassifier()
        self.clf.fit(self.X, self.y)

        self.importances = self.clf.feature_importances_
        self.indices = np.argsort(self.importances)
        self.features = list(self.X.columns)
        self.sorted_features = [self.features[i] for i in self.indices]

    def get_features(self):
        return self.importances, self.indices, self.sorted_features