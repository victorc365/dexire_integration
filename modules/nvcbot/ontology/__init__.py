import owlready2
import pathlib
from lxml import etree as ET
from application import ONTOLOGY_DIR, ONTOLOGY_FILE
import pickle
from anytree import Node
from anytree.exporter import DictExporter
import itertools
import typing as t

ONTOLOGY_DIR = pathlib.Path(__file__).parent

onto: owlready2.Ontology = owlready2.get_ontology(
    str(ONTOLOGY_DIR / "ontology.owl")).load()

def expand_classes(list_of_input_classes: t.List) -> t.List:
    list_of_classes = [onto[item_class] for item_class in list_of_input_classes]
    list_of_input_classes.extend(
        [item.name for item in itertools.chain.from_iterable(
        [food_class.subclasses() 
         for food_class in list_of_classes 
         if isinstance(food_class, owlready2.ThingClass)])
        ])
    return list_of_input_classes


def get_users_ontology_dict():
    users = list(onto.User.subclasses())
    user_to_onto = {}
    for user in users:
        user_to_onto[user.name.lower()] = user

    return user_to_onto

def get_ontology_ingredients(uuid):
    parser = ET.XMLParser(remove_blank_text=True)
    test_tree = ET.parse(ONTOLOGY_FILE, parser)
    test_root = test_tree.getroot()
    
    try:
        with open(f'./cache/user_profiles/{uuid}.pkl', 'rb') as handle:
            user_profile = pickle.load(handle)
    except FileNotFoundError as err:
        user_profile = None

    user_habits_does_not_eat = [
        category
        for user_habit in [get_users_ontology_dict()[habit.lower()] for habit in user_profile["habits"]]
        for category in user_habit.doesNotEat] if user_profile else []

    select_node = Node("Food")
    nodes = {"Food": select_node}

    stack = [(select_node, subclass)
             for subclass in list(onto.Food.subclasses())]

    while stack:
        for (parent, item) in stack:
            if item.name == "Recipe":
                stack.remove((parent, item)) 
                continue
            if item not in user_habits_does_not_eat:
                stack.extend([(item, subclass)
                             for subclass in list(item.subclasses())])
                item_name = item.name.replace("_", " ")
                parent_name = parent.name.replace("_", " ")
                nodes[item_name] = Node(item_name, parent=nodes[parent_name])
            stack.remove((parent, item))

    exporter = DictExporter(dictcls=dict, attriter=sorted)

    structured_class = {}
    for x in test_root.findall(".//{http://www.w3.org/2002/07/owl#}ClassAssertion"):
        main_class = x.find(".//{http://www.w3.org/2002/07/owl#}Class")
        main_class_name = main_class.attrib['IRI'].replace(
            "#", "").replace("_", " ")

        if main_class_name not in nodes:
            continue

        individual = x.find(
            ".//{http://www.w3.org/2002/07/owl#}NamedIndividual")
        individual_name = individual.attrib['IRI'].replace(
            "#", "").replace("_", " ")

        tmp_list = structured_class.get(main_class_name, [])
        tmp_list.append(individual_name)
        structured_class[main_class_name] = tmp_list

    return structured_class, exporter.export(select_node)