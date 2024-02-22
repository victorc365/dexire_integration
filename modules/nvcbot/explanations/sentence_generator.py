import random

# Phrases for reasons
reasons = [
    "because", "as it", "due to the fact that", "owing to the reason that",
    "for the reason that", "on account of the fact that", "in view of the fact that",
    "considering that", "since", "given that", "seeing that", "taking into account that",
    "thanks to", "on the grounds that", "in light of the fact that", "based on the fact that",
    "in consideration of the fact that", "as a result of", "because of the fact that",
    "with the intention that", "with the purpose that", "with the aim that", "in order to",
    "so as to", "for the purpose of", "for the intention of", "with the goal of",
    "with the objective of", "with the desire of", "with the plan of"
]

# Phrases for taste adjectives
adjectives_taste = [
    "delicious", "mouthwatering", "scrumptious", "delectable", "flavorful", "tasty",
    "yummy", "appetizing", "savory", "tempting", "palatable", "satisfying",
    "luscious", "succulent", "irresistible", "divine", "heavenly", "exquisite",
    "gorgeous", "finger-licking", "delightful", "pleasing", "enjoyable", "savorous",
    "mouth-pleasing", "tongue-tingling", "tantalizing", "sumptuous", "mouth-filling",
    "enthralling", "mouth-gasmic"
]

# Phrases for "but"
phrases_but = [
    "However", 
    "But", 
    "Yet", 
    "instead"
]
'''
    "In contrast,", "Despite that,", "In spite of that,", "Notwithstanding,",
    "Conversely,", "On the flip side,", "Alternatively,", "Although,", "In any case,",
    "Notwithstanding the above,", "That being said,", "In spite of this,", "However,",
    "Nonetheless,", , "Regardless,", "In either case,",
    "In other words,", "To the contrary,", "By way of contrast,", "In a different vein,",
    "At the same time,", "In a similar vein,"
'''


# Phrases for "you dislike" attribute
phrases_dislike = ["you will dislike it", "it won't be to your taste", "it won't be your preference", "it won't be appealing to you", "it won't be your cup of tea", "it won't be your thing", "it won't be what you're looking for", "it won't be your style", "it won't be your favorite", "it won't be something you enjoy", "it won't be something you would choose", "it won't be your ideal choice", "it won't be your kind of recipe", "it won't be what you would go for", "it won't be on your list of favorites", "it won't be something you would recommend", "it won't be something that suits your palate", "it won't be your preferred flavor", "it won't be something you would prefer", "it won't be your go-to option", "it won't be something that you find appealing", "it won't be your desired taste", "it won't be something you have a liking for", "it won't be something that you would enjoy", "it won't be something you would rate highly", "it won't be something that matches your preferences", "it won't be something that you find satisfying", "it won't be something you would choose again", "it won't be something you would typically enjoy", "it won't be something that you find appetizing"]
# Phrases for "it contains" attribute
phrases_contains = ["it contains", "it includes", "it incorporates", "it features", "it has", "it boasts", "it offers", "it presents", "it comprises", "it involves", "it incorporates", "it encompasses", "it holds", "it possesses", "it carries", "it contains within", "it consists of", "it contains a combination of", "it contains a mix of", "it contains a variety of", "it contains a diverse range of", "it contains an assortment of", "it contains an array of", "it contains an abundance of", "it contains a generous amount of", "it contains a substantial quantity of", "it contains a significant level of", "it contains a rich content of", "it contains a high proportion of"]

# Phrases for recommendations
recommendations = [
    "We would like to recommend", "We would like to suggest", "We would like to advise", "We would like to propose", "We would like to encourage", "We would like to urge",
    "We would like to endorse", "We would like to vouch for", "We would like to advocate for", "We would like to stand by", "We would like to support", "We would like to back",
    "We would like to promote", "We would like to champion", "We would like to approve", "We would like to applaud", "We would like to venerate", "We would like to extol",
    "We would like to celebrate", "We would like to validate", "We would like to commend", "We would like to laud", "We would like to esteem", "We would like to admire",
    "We would like to value", "We would like to prize", "We would like to cherish", "We would like to treasure", "We would like to honor", "We would like to respect"
]

counter_recommend = [
    "As an alternative, we can suggest",
    "Instead, we can recommend",
    "Alternatively, we can advise you to eat",
    "Another option is to recommend",
    "We have the option to suggest instead",
    "In an alternative approach, we can recommend",
    "We can also propose as an alternative",
    "As a different suggestion, we could recommend",
    "Alternatively, we can offer the recipe ",
    "In a different vein, we could suggest",
]


phrases = {
    # Phrases for calorie content
    "calories": [
        "is low in calories", "offers a light and calorie-conscious option", "is a guilt-free choice with fewer calories",
        "contains a moderate amount of calories", "is calorie-friendly", "is a calorie-conscious recipe",
        "is a low-calorie alternative", "is a recipe with controlled calorie levels", "is a recipe with a modest calorie content",
        "is a recipe that keeps calories in check", "is a recipe with mindful calorie usage", "is a recipe with a balanced calorie profile",
        "is a recipe with a restrained calorie content", "is a recipe with carefully measured calories",
        "is a recipe with calorie awareness", "is a recipe with a calorie-savvy approach",
        "is a recipe with a calorie-conscious mindset", "is a recipe with an eye on calorie content",
        "is a recipe with calories taken into consideration", "is a recipe that promotes calorie control",
        "is a recipe that supports a calorie-friendly diet", "is a recipe that contributes to a healthy calorie intake",
        "is a recipe that prioritizes low calorie consumption", "is a recipe that helps manage calorie intake",
        "is a recipe that aids in calorie control", "is a recipe that assists in calorie reduction",
        "is a recipe that is mindful of calorie impact", "is a recipe that helps maintain a balanced calorie intake",
        "is a recipe that encourages portion control for calorie management"],

    "carbs": [
        "Has a favorable carbohydrate profile",
        "Provides a healthy amount of carbohydrates",
        "Offers a nutritious carbohydrate content",
        "Contains beneficial carbohydrates for health",
        "Presents a carb composition that promotes wellness",
        "Boasts a healthy carbohydrate composition",
        "Delivers a nourishing carbohydrate profile",
        "Features a favorable carbohydrate balance",
        "Comes with a healthful amount of carbohydrates",
        "Provides a beneficial level of carbohydrates for a healthy diet",
    ],
    # Phrases for "recipe"
    "recipe": [
        "this recipe", "this dish", "this meal idea", "this cooking masterpiece", "this culinary creation",
        "this gastronomic delight", "this food concoction", "this plate", "this culinary gem",
        "this delicacy", "this epicurean treat", "this feast", "this flavorful creation",
        "this gourmet dish", "this kitchen marvel", "this palate pleaser", "this savory creation",
        "this tasty option", "this delectable invention", "this delicious masterpiece",
        "this succulent delight", "this tantalizing recipe", "this mouthwatering suggestion",
        "this culinary wonder", "this epicurean delight", "this flavorsome delight",
        "this scrumptious offering", "this delectable choice", "this culinary specialty",
        "this culinary marvel"
    ],
    # Phrases for average rating
    "avg_rate": [
        "has received outstanding reviews", "is highly rated by our customers", "is well-loved by food enthusiasts",
        "has garnered rave reviews", "is a customer favorite", "is top-rated", "receives glowing recommendations",
        "has an excellent reputation", "is highly regarded", "is praised for its quality", "is consistently rated highly",
        "is applauded for its taste", "is a crowd-pleaser", "has won over many hearts", "is highly recommended",
        "is renowned for its flavor", "is widely acclaimed", "is a beloved recipe", "has a stellar track record",
        "is known for its exceptional taste", "has been hailed as a culinary masterpiece", "is celebrated for its excellence",
        "is a standout choice", "has earned its place among the best", "is a tried-and-true favorite",
        "has a strong following", "is celebrated for its deliciousness", "is revered for its quality and flavor",
        "is a top-notch option", "has been praised for its culinary artistry"],
    # Phrases for preparation time
    "PrepTime": [  
        "requires minimal preparation time", "is quick and easy to prepare", "takes little time to prepare",
        "is a breeze to get ready", "can be prepared in a matter of minutes", "is hassle-free to prep",
        "saves you valuable time in the kitchen", "is perfect for busy individuals", "fits well into a hectic schedule",
        "allows for efficient meal preparation", "simplifies the cooking process", "requires minimal effort to make",
        "streamlines the preparation steps", "is designed for easy and quick cooking", "is a time-saving option",
        "is perfect for those short on time", "lets you enjoy a delicious meal without spending too much time cooking",
        "is a convenient choice for quick meals", "is ideal for those with a busy lifestyle", "is a time-friendly option",
        "offers a shortcut to a satisfying meal", "saves precious minutes in the kitchen", "is a go-to for quick and tasty meals",
        "is tailored for busy schedules", "ensures a swift and enjoyable cooking experience", "is a time-savvy choice",
        "is a time-efficient option", "provides a quick and delicious solution", "is perfect for time-strapped individuals",
        "is a smart choice for those in a hurry"],

    # Phrases for cooking time
    "CookingTime": [
        "cooks up quickly", "requires minimal cooking time", "is ready in no time", "is a quick-cooking recipe",
        "saves cooking time", "is ideal for busy schedules", "allows for efficient meal preparation",
        "is a time-friendly option", "is a convenient choice for quick meals", "is perfect for fast-paced lifestyles",
        "is a time-saving solution", "lets you enjoy a delicious meal without spending too much time cooking",
        "is a speedy option for satisfying your cravings", "cuts down on cooking time without compromising flavor",
        "is tailored for those who value efficiency in the kitchen", "minimizes the time spent at the stove",
        "is a time-savvy choice for cooking enthusiasts", "lets you enjoy a home-cooked meal without the wait",
        "simplifies mealtime with its quick cooking process", "allows for more time to savor and enjoy the meal",
        "is a go-to option for those looking to minimize their time in the kitchen", "is a time-efficient choice",
        "is a time-smart solution for delicious results", "offers a rapid cooking experience",
        "is designed to save you precious minutes during meal preparation", "is perfect for those with a busy schedule",
        "is a time-conscious choice", "gets you to the table faster with its efficient cooking time",
        "ensures you can enjoy a tasty meal without sacrificing too much time in the kitchen"
        ],
    # Phrases for oven temperature
    "oven_temp": [
        "requires a moderate oven temperature", "should be cooked at a low oven temperature",
        "needs a high oven temperature", "calls for a preheated oven", "should be baked in a preheated oven",
        "requires a precise oven temperature control", "needs an oven temperature adjustment",
        "should be cooked at a specific oven temperature", "requires an oven temperature of",
        "should be baked at", "needs to be set at an oven temperature of", "should be heated to an oven temperature of",
        "should be roasted at an oven temperature of", "should be broiled at an oven temperature of",
        "should be grilled at an oven temperature of", "should be baked on high heat", "should be baked on low heat",
        "should be cooked at a gentle oven temperature", "should be slow-cooked at a low oven temperature",
        "should be cooked at a steady oven temperature", "should be baked at a controlled oven temperature",
        "should be roasted at a medium oven temperature", "should be broiled at a high oven temperature",
        "should be grilled at a medium-high oven temperature", "should be baked at a moderate heat",
        "should be cooked at a consistent oven temperature", "should be slow-roasted at a low oven temperature",
        "should be cooked at a specific temperature setting", "should be baked at a carefully regulated oven temperature"],

    # Phrases for sugar content
    "sugar":[
        "has a low sugar content", "contains minimal amounts of sugar", "is low in sugar",
        "is not overly sweet", "offers a reduced sugar option", "is a healthier choice with less sugar",
        "contains a small amount of sugar", "is sugar-conscious", "is a low-sugar alternative",
        "is a sugar-reduced recipe", "is sweetened moderately", "is not excessively sweet",
        "is a sugar-friendly option", "is a recipe with controlled sugar levels",
        "is a recipe with a modest sugar content", "is sweetened sparingly", "has a limited sugar quantity",
        "contains a moderate amount of sugar", "is not overly sugary", "is a sugar-aware choice",
        "is a recipe with mindful sugar usage", "is a recipe with a balanced sugar profile",
        "is a recipe with a restrained sugar presence", "is a recipe with carefully measured sugar",
        "is a recipe with a controlled sweetness", "is a recipe with sugar taken into consideration",
        "is a recipe with sugar awareness", "is a recipe with a sugar-conscious approach",
        "is a recipe with a sugar-savvy mindset", "is a recipe with an eye on sugar content"],

    "fiber":[
        "has a high amount of fiber",
        "contains a substantial fiber content",
        "provides a noteworthy quantity of dietary fiber",
        "offers a considerable amount of fiber",
        "includes a significant fiber content",
        "comes with a plentiful supply of dietary fiber",
        "boasts a notable amount of fiber",
        "presents a substantial fiber concentration",
        "delivers a high proportion of dietary fiber",
        "contains a substantial fiber level",
        "features a generous amount of fiber content" ,
        ],

    "fat":[
        "Contains an appropriate fat content",
        "Offers a beneficial level of fat",
        "Includes a healthful amount of fat",
        "Provides a balanced fat content",
        "Has a good quantity of healthy fat",
        "Presents a suitable fat level",
        "Comes with a favorable fat amount",
        "Delivers a proper fat content",
        "Boasts a well-balanced fat level",
        "Features an adequate amount of healthy fat",
        ],

    # Phrases for cholesterol content
    "cholesterol": [
        "has a low cholesterol content", "is cholesterol-free", "contains no cholesterol",
        "is a heart-healthy choice with minimal cholesterol", "offers a reduced cholesterol option",
        "is a cholesterol-conscious recipe", "is a low-cholesterol alternative",
        "is a recipe with controlled cholesterol levels", "is a recipe with a modest cholesterol content",
        "is cholesterol-friendly", "is a cholesterol-reduced recipe",
        "is a recipe with minimal cholesterol presence", "is a recipe with limited cholesterol",
        "is a recipe with mindful cholesterol usage", "is a recipe with a balanced cholesterol profile",
        "is a recipe with a restrained cholesterol content", "is a recipe with carefully measured cholesterol",
        "is a recipe with cholesterol awareness", "is a recipe with a cholesterol-savvy approach",
        "is a recipe with a cholesterol-conscious mindset", "is a recipe with an eye on cholesterol content",
        "is a recipe with cholesterol taken into consideration", "is a recipe with cholesterol in mind",
        "is a recipe that keeps cholesterol levels in check", "is a recipe that promotes heart health",
        "is a recipe that supports a cholesterol-friendly diet", "is a recipe that contributes to a healthy cholesterol profile",
        "is a recipe that prioritizes low cholesterol intake", "is a recipe that is mindful of cholesterol impact"],

    # Phrases for protein content
    "protein": [
       "is protein-rich", "contains a high amount of protein", "is packed with protein",
       "is a great source of protein", "offers a generous protein content",
       "is protein-packed", "provides ample protein", "is protein-dense",
       "is an excellent protein source", "is loaded with protein",
       "is rich in high-quality protein", "is a protein powerhouse",
       "is a protein-focused recipe", "is a protein-forward option",
       "is a recipe that prioritizes protein intake", "is a protein-driven choice",
       "is a recipe that supports a high-protein diet", "is a recipe that emphasizes protein",
       "is a recipe that delivers on protein", "is a recipe that boosts protein intake",
       "is a recipe that promotes muscle-building", "is a recipe that aids in protein synthesis",
       "is a recipe that contributes to a protein-rich diet", "is a recipe that is abundant in protein",
       "is a recipe that adds protein to your meals", "is a recipe that satisfies your protein needs",
       "is a recipe that helps meet your daily protein requirements", "is a recipe that fuels with protein",
       "is a recipe that enhances protein consumption"],
    "ingredient_matching_score": [
        "aligns with your taste preferences",
        "is tailored to suit your preferences",
        "caters to your individual taste",
        "is a recipe that matches your personal preferences",
        "is customized to your liking",
        "is designed to accommodate your preferences",
        "is a recipe that suits your specific taste",
        "is crafted to fit your personal preferences",
        "is well-suited to your individual liking",
        "is a recipe that perfectly matches your preferences",
    ],
    "cuisine_matching_score": [
        "aligns with your taste preferences",
        "is tailored to suit your preferences",
        "caters to your individual taste",
        "is a recipe that matches your personal preferences",
        "is customized to your liking",
        "is designed to accommodate your preferences",
        "is a recipe that suits your specific taste",
        "is crafted to fit your personal preferences",
        "is well-suited to your individual liking",
        "is a recipe that perfectly matches your preferences",
    ],
    "final_matching_score": [
        "aligns with your taste preferences",
        "is tailored to suit your preferences",
        "caters to your individual taste",
        "is a recipe that matches your personal preferences",
        "is customized to your liking",
        "is designed to accommodate your preferences",
        "is a recipe that suits your specific taste",
        "is crafted to fit your personal preferences",
        "is well-suited to your individual liking",
        "is a recipe that perfectly matches your preferences",
    ],
    "health_score": [
        "Is typically better for your health",
        "Tends to be more healthful for you",
        "Is generally considered healthier for you",
        "Promotes overall better health",
        "Offers a healthier option for you",
        "Contributes to your well-being in general",
        "Prioritizes your health and well-being",
        "Supports your overall health",
        "Is a healthier choice for your well-being",
        "Helps improve your overall health",
    ],
    }

expanded = {
'calories': "Calories are necessary to provide energy for bodily functions and physical activities, but they need to be balanced because consuming excessive calories can lead to weight gain and associated health issues such as obesity, while consuming too few calories can result in nutrient deficiencies and inadequate energy levels.",
'carbs': "Carbohydrates are a primary source of energy for the body, supporting brain function, physical performance, and fueling various metabolic processes, but they need to be balanced because consuming excessive carbohydrates, particularly refined ones, can contribute to weight gain, insulin resistance, and an increased risk of chronic diseases, while insufficient carbohydrate intake can lead to low energy levels and nutrient deficiencies.",
'PrepTime': None,
'CookingTime': None,
'oven_temp': None,
'fiber': "Fiber is important for maintaining a healthy digestive system, promoting regular bowel movements, lowering cholesterol levels, regulating blood sugar levels, aiding in weight management, and reducing the risk of developing chronic diseases such as heart disease, diabetes, and certain types of cancer.",
'fat': "Fats are essential for the body as they provide a concentrated source of energy, support the absorption of fat-soluble vitamins, help maintain healthy cell function, contribute to hormone production, and ensure proper insulation and protection of organs, but it's crucial to maintain a balanced intake to avoid negative health effects such as weight gain and increased risk of cardiovascular diseases.",
'cholesterol': "Cholesterol is essential for various bodily functions, including hormone synthesis, cell membrane structure, and production of vitamin D, but it needs to be balanced because excessive levels of cholesterol can lead to the formation of plaque in the arteries, increasing the risk of heart disease and other cardiovascular problems.",
'protein': "Proteins are beneficial for the body due to their role in supporting tissue repair, promoting muscle growth and maintenance, facilitating enzyme production for metabolic processes, aiding in hormone regulation, contributing to a healthy immune system, and providing a source of essential amino acids necessary for overall health and well-being.",
'final_matching_score': "",
'health_score': ""
}

# ["calories", "fat", "carbs", "protein", "fiber", "final_matching_score", "health_score", "recommended"]

def get_single_food_fact(factor: str):
    return " ".join([random.choice(phrases["recipe"]), random.choice(phrases[factor]).lower()]).capitalize(), expanded[factor]

def get_sentence(factors: tuple[str]):
    sentence = random.choice(recommendations)
    for factor in factors:
        sentence += " " + random.choice(phrases[factor])
    return sentence

def get_counter_sentence(strong_item_factors, weak_item_factors, recommended_recipe, counter_recipe):
    counter_recipe_name: str = counter_recipe.title
    recommended_recipe_name: str = recommended_recipe.title

    print(phrases.keys())

    strong_factor_phrases = [random.choice(phrases[factor]) for factor in strong_item_factors]
    weak_factor_phrases = [random.choice(phrases[factor]) for factor in weak_item_factors]

    potential_sentences = []
    recommendation_tags = list(counter_recipe.recommendation_tags)
    if weak_factor_phrases and (recommendation_tags and "UNHEALTHY_RECIPE" not in recommendation_tags):
        unrecommend_reason = random.choice(recommendation_tags)

        potential_sentences.append(" ".join([
            random.choice(counter_recommend),
            counter_recipe_name.title(),
            "given that it", 
            " and ".join(weak_factor_phrases).lower() + ",",
            random.choice(phrases_but).lower() + ",",
            "we recommend",
            recommended_recipe_name.title(),
            "since you dislike the former's",
            unrecommend_reason.split("_")[1].lower()
        ]))

    if weak_factor_phrases and (recommendation_tags and "UNHEALTHY_RECIPE" in recommendation_tags):
        potential_sentences.append(" ".join([
            random.choice(counter_recommend),
            counter_recipe_name.title(),
            "given that it", 
            " and ".join(weak_factor_phrases).lower() + ",",
            random.choice(phrases_but).lower() + ",",
            "we recommend",
            recommended_recipe_name.title(),
            "since the former is unhealthier",
        ]))

    if strong_factor_phrases:
        potential_sentences.append(" ".join([
            random.choice(counter_recommend),
            counter_recipe_name.title() + ",",
            random.choice(phrases_but).lower() + ",",
            "we recommend",
            recommended_recipe_name.title(),
            "given that it", 
            " and it ".join(strong_factor_phrases).lower()
            ]))

    return random.choice(potential_sentences)


