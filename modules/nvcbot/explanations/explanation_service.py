from dexire.core.rule_set import RuleSet
import bnlearn as bn
import pandas as pd

class ExplanationService:
    def __init__(self, path_rule_set, path_bayesian_model):
        print("Loading explainers...")
        self.rule_set = RuleSet.load(path_rule_set)
        self.bayesian_model = bn.load(path_bayesian_model)
        
    def generate_rule_based_explanation(self, data: pd.DataFrame) -> str:
        if self.rule_set is None:
            return "No explainers loaded."
        else:
            explanation = self.rule_set.numpy_predictions(data,
                                                          return_rules=True)
            
    def generate_probabilistic_explanation(self, data: pd.DataFrame) -> str:
        if self.bayesian_model is None:
            return "No Bayesian model loaded."
        else:
            explanation = bn.inference.get_cpds(self.bayesian_model,
                                               data=data,
                                               type='cpd',
                                               show_errors=False)
            
        return explanation.to_dict()
                                        