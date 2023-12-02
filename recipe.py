from typing import Dict, Tuple
from bs4.element import Tag


from web import get_soup_from_url, get_raw_ingredients_from_soup, get_raw_steps_from_soup
from sentence_helper import raw_steps_to_list_sentences

from ingredient import parse_ingredients, get_ingredients_names
from step import parse_steps, parse_methods, parse_tools, Action

class Recipe:
    def __init__(self, url: str) -> None:
        soup, self.recipe_name = get_soup_from_url(url)
        raw_ingredients = get_raw_ingredients_from_soup(soup)
        raw_steps = get_raw_steps_from_soup(soup)
        sentences_list = raw_steps_to_list_sentences(raw_steps) # each step is a list of sentences
        self.ingredients = parse_ingredients(raw_ingredients)
        self.ingredients_names = get_ingredients_names(self.ingredients)
        self.steps = parse_steps(sentences_list, self.ingredients_names)
        # for testing purposes
        self.temp_steps=sentences_list

        self.tools = parse_tools(self.steps)
        self.methods = parse_methods(self.steps)
        self.num_actions = sum([len(sentences) for sentences in sentences_list])
        self.action_idx_to_idx_tuple = self.make_idx_tuple_dict()
        
    def print_abstract(self) -> None:
        print(f"Recipe name: {self.recipe_name}")
        print(f"Number of actions: {self.num_actions}")
        print(f"Ingredients: {', '.join(self.ingredients_names)}")
        print(f"Tools: {', '.join(self.tools)}")
        print(f"Methods: {', '.join(self.methods)}")
        print(self.action_idx_to_idx_tuple)
    
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
        print(f"Method: {', '.join(action.method)}")
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
    url = "https://www.allrecipes.com/air-fryer-ham-and-cheese-wraps-recipe-8365118"
    # url = "https://www.allrecipes.com/recipe/12151/banana-cream-pie-i/"
    # url = "https://www.allrecipes.com/recipe/217331/goan-pork-vindaloo/"
    recipe = Recipe(url)
    # print(recipe.tools)
    # print(recipe.methods)
    
    
