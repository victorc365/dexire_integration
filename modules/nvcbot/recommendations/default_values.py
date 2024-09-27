# dictionary allergy queries with synonyms
allergies_queries_dict = {'tree nuts': ['tree', 'nuts', 'nut', 'tree nuts'],
                          'wheat': ['wheat', 'grain', 'gluten'],
                          'eggs': ['eggs', 'egg'],
                          'soy': ['soy', 'soya', 'Glycine max'],
                          'fish': ['fish', 'salmon', 'seafood', 'tuna'],
                          'peanut': ['peanut', 'groundnut', 'mani'],
                          'shellfish': ['shellfish', 'clam', 'lobster', 'scallop', 'mollusk', 'snail'],
                          "cow's milk": ["cow's milk", "milk", "lactose"],
                          "NotAllergy": []}

cultural_factors = {
    "vegan_observant": [True, False],
    "vegetarian_observant": [True, False],
    "halal_observant": [True, False],
    "kosher_observant": [True, False],
    "flexi_observant": [True, False],
    "NotRestriction": []
}

# Calorie distribution across meals
meals_calorie_dict = {"breakfast": 0.3,
                      "morning snacks": 0.05,
                      "afternoon snacks": 0.05,
                      "lunch": 0.4,
                      "dinner": 0.2
                      }

flexi_probabilities_dict = {
    "flexi_vegan": {
        "vegan_observant": 0.60,
        "vegetarian_observant": 0.20,
        "halal_observant": 0.10,
        "kosher_observant": 0.1,
        "None": 0.0
    },
    "flexi_vegetarian": {
        # no meaningful flexi for this class:
        # vegetarian -> vegan
        "vegan_observant": 0.00,
        "vegetarian_observant": 0.60,
        "halal_observant": 0.0,
        "kosher_observant": 0.1,
        "None": 0.30
    },
    "flexi_halal": {
        "vegan_observant": 0.1,
        "vegetarian_observant":  0.2,
        "halal_observant": 0.6,
        "kosher_observant": 0.0,
        "None": 0.1
    },
    "flexi_kosher": {
        "vegan_observant": 0.1,
        "vegetarian_observant": 0.1,
        "halal_observant": 0.1,
        "kosher_observant": 0.6,
        "None": 0.1
    }
}

place_proba_dict = {
    "restaurant": 0.3,
    "home": 0.5,
    "outdoor": 0.2
}

social_situation_proba_dict = {
    "alone": 0.3,
    "family": 0.3,
    "friends": 0.2,
    "colleagues": 0.2
}

time_options = {
    "now": "time_now",
    "in one hour": "time_in_one_hour",
    "in two hours": "time_in_two_hours",
    "other time": "other_time"
}

user_entity = {
    "current_working_status": ["Half-time-worker", "Full-time-worker", "Self-employee", "Unemployed"],
    "marital_status": ["Single", "Married"],
    "life_style": ["Sedentary", "Lightly active", "Moderately active", "Very active"],
    "weight": [],
    "ethnicity": ["White", "Black", "Latino", "Asian"],
    "height": []
}