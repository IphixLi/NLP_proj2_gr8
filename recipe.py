from typing import Dict, Tuple, List
from bs4.element import Tag


from web import get_soup_from_url, get_raw_ingredients_from_soup, get_raw_steps_from_soup
from sentence_helper import raw_steps_to_list_sentences

from ingredient import parse_ingredients, get_ingredients_names, Ingredient
from step import parse_steps,parse_original_ingredients, parse_methods, parse_tools, Action
from quantity_transformation import transform_quantity
from transformation import transform_recipe_type

class Recipe:
    def __init__(self, url: str) -> None:
        soup, self.recipe_name = get_soup_from_url(url)
        raw_ingredients = get_raw_ingredients_from_soup(soup)
        raw_steps = get_raw_steps_from_soup(soup)
        sentences_list = raw_steps_to_list_sentences(raw_steps) # each step is a list of sentences
        self.sentences_list = sentences_list
        self.ingredients = parse_ingredients(raw_ingredients)
        self.ingredients_names = get_ingredients_names(self.ingredients)
        self.steps = parse_steps(sentences_list, self.ingredients_names)
        # for testing purposes
        self.temp_steps=sentences_list

        self.tools = parse_tools(self.steps)
        self.methods = parse_methods(self.steps)
        self.prime, self.verbs = self.methods
        self.num_actions = sum([len(sentences) for sentences in sentences_list])
        self.action_idx_to_idx_tuple = self.make_idx_tuple_dict()
        self.modification=None
    
    def transform(self, new_sentences_list: List[List[str]], new_ingredients: List[Ingredient], modification:str='') -> None:
        self.sentences_list = new_sentences_list
        self.ingredients = new_ingredients
        self.ingredients_names = get_ingredients_names(self.ingredients)
        self.steps = parse_steps(new_sentences_list, self.ingredients_names)
        
        self.tools = parse_tools(self.steps)
        self.methods = parse_methods(self.steps)
        self.prime, self.verbs = self.methods
        self.num_actions = sum([len(sentences) for sentences in new_sentences_list])
        self.action_idx_to_idx_tuple = self.make_idx_tuple_dict()
        
        if self.modification:
            recipe_name=self.recipe_name.split(" (")[0]
        else:
            recipe_name=self.recipe_name
            
        if modification:
            self.modification=modification
            self.recipe_name=recipe_name + ' ( ' + modification + ' )'
        else:
            self.modification=''
            self.recipe_name=recipe_name
        
    def print_abstract(self) -> None:
        print(f"Recipe name: {self.recipe_name}")
        print(f"Number of actions: {self.num_actions}")
        print(f"Ingredients: {', '.join(self.ingredients_names)}")
        print(f"Tools: {', '.join(self.tools)}")
        print(f"Primary cooking method: {', '.join(self.prime)}")
        print(f"Other cooking methods: {', '.join(self.verbs)}")
    
    def print_ingredients(self) -> None:
        for ingredient in self.ingredients:
            print(ingredient)
    
    def make_idx_tuple_dict(self) -> Dict[int, Tuple[int, int]]:
        idx_tuple_dict = {}
        for step_idx, step in enumerate(self.steps):
            for sentence_idx, _ in enumerate(step.actions):
                idx_tuple_dict[len(idx_tuple_dict)] = (step_idx, sentence_idx)
        return idx_tuple_dict
    
    def print_action(self, action_index: int) -> None:
        step_idx, cur_action_idx = self.action_idx_to_idx_tuple[action_index]
        action = self.steps[step_idx].actions[cur_action_idx]
        
        print(action.sentence)
        print()
        if action.temperature:
            print(f"Temperature: {action.temperature}")
        print(f"Ingredients: {', '.join(action.ingredients)}")
        if action.time:
            print(f"Time: {action.time}")
        print(f"Primary cooking method: {', '.join(action.method[0])}")
        print(f"Other cooking methods: {', '.join(action.method[1])}")
        print(f"Tools: {', '.join(action.tools)}")
    
    def get_action(self, action_index: int) -> Action:
        step_idx, cur_action_idx = self.action_idx_to_idx_tuple[action_index]
        return self.steps[step_idx].actions[cur_action_idx]
    
    def list_actions(self) -> None:
        for i, index_tuple in enumerate(self.action_idx_to_idx_tuple.values()):
            step_idx, cur_action_idx = index_tuple
            print(f"Step {i+1}: {self.steps[step_idx].actions[cur_action_idx].sentence}")
    
    
if __name__ == "__main__":
    # url = "https://www.allrecipes.com/recipe/12151/banana-cream-pie-i/"
    # url = "https://www.allrecipes.com/air-fryer-ham-and-cheese-wraps-recipe-8365118"
    # url = "https://www.allrecipes.com/recipe/12151/banana-cream-pie-i/"
    # url = "https://www.allrecipes.com/recipe/217331/goan-pork-vindaloo/"
    url = "https://www.allrecipes.com/recipe/51326/chinese-tea-leaf-eggs/"
    recipe = Recipe(url)
    recipe.list_actions() # check actions
    recipe.print_ingredients() # check ingredients
    recipe.print_abstract() # check methods and tools
    
    print()
    print()
    
    # TODO: test transform here
    # STEP 1: generate new sentences_list and ingredients_list
    # two options: call transform_quantity on 1. the entire recipe object (you can access any data you want) or 2. on the sentences_list and ingredients_list
    # (see the input type of both options in quantity_transformation.py)
    # option 1 (use deepcopy!)
    new_sentences_list, new_ingredients = transform_quantity(recipe, 0.5)
    # option 2
    # new_sentences_list, new_ingredients = transform_quantity(recipe.sentences_list, recipe.ingredients, 0.5)
    
    # STEP 2: use the new sentences_list and ingredients_list to create a new recipe object
    recipe.transform(new_sentences_list, new_ingredients)
    
    new_sentences_list_type, new_ingredients_type = transform_recipe_type(recipe, 'healthy')
    recipe.transform(new_sentences_list_type, new_ingredients_type,modification='healthy')
    
    # print("modified_ingredients: ",new_ingredients_type)
    # print("-----------------------------")
    # print("modified_sentences: ",new_sentences_list_type)

    recipe.list_actions()
    recipe.print_ingredients()
    recipe.print_abstract()
