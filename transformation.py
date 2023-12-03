from fuzzywuzzy import fuzz
from transformationDB import transformations
from typing import List, Tuple
from ingredient import Ingredient
from step import parse_original_ingredients


def transform_recipe_type(recipe, transformation_type: str) -> Tuple[List[List[str]], List[Ingredient]]:
    sentences_list = recipe.sentences_list  # List[List[str]]
    ingredients_list = recipe.ingredients   # List[Ingredient]
    ingredient_names= recipe.ingredients_names 
    transformation_dict=transformations[transformation_type]

    # print("ingredient_list: ", ingredients_list)

    ingredient_mappings=parse_original_ingredients(sentences_list, ingredient_names)

    print("mappings: ", ingredient_mappings)
    new_sentences_list=transform_sentence_list( sentences_list,transformation_dict,ingredient_mappings)
    new_ingredients_list=transform_ingredient_list( ingredients_list,transformation_dict, ingredient_mappings)

    return new_sentences_list, new_ingredients_list


def transform_ingredient_list(ingredient_list:List[Ingredient], transformation_dict:dict, ingredient_mappings:dict):
    # modify self.name, self.preparation??
    new_ingredients_list=[]
    for ingredient in ingredient_list:
        new_ingredient= ingredient
        # find matching ingredient in transformations
        matching_ingredient = transform_ingredient(ingredient.name,transformation_dict)
        if matching_ingredient!=ingredient.name:
            new_ingredient.update_name(matching_ingredient)
        elif ingredient.name in ingredient_mappings.values():
            raw_name=get_first_key_by_value(ingredient_mappings, ingredient.name)
            match_from_original= transform_ingredient(raw_name,transformation_dict)
            if match_from_original!=ingredient.name:
                new_ingredient.update_name(match_from_original)

        new_ingredients_list.append(new_ingredient)
    return new_ingredients_list

# transformation for sentence list
def transform_sentence_list( sentence_list,transformation_dict, ingredient_mappings:dict):
    new_sentence_list = []

    for step in sentence_list:
        step_list = []
        for sentence in step:
            new_sentence = sentence
            for key, value in ingredient_mappings.items():
                from_official_name = transform_ingredient(value, transformation_dict)
                new_sentence = new_sentence.replace(value, from_official_name)
                
                from_raw_name = transform_ingredient(key, transformation_dict)
                new_sentence = new_sentence.replace(key, from_raw_name)
            step_list.append(new_sentence)
        new_sentence_list.append(step_list)

    # print("new: ", new_sentence_list, sentence_list)
    return new_sentence_list
        
def transform_ingredient(ingredient, transformation_dict):
    matching_ingredient = find_closest_match(ingredient, transformation_dict)
    if matching_ingredient:
        return matching_ingredient
    else:
        return ingredient
def find_closest_match(input_key, substitution_list):
    closest_match, match_val= max(substitution_list.items(), key=lambda x: fuzz.ratio(x[0], input_key))
    
    # You can adjust the threshold based on your preferences\
    similarity=fuzz.ratio(closest_match, input_key)
    # print("test??", input_key, ",", closest_match,",", match_val, similarity )
    if similarity > 70:
        return match_val
    else:
        return None

def get_first_key_by_value(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key
    return None