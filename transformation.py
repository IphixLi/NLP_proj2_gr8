from fuzzywuzzy import fuzz
from transformationDB import transformations
from typing import List, Tuple
from ingredient import Ingredient
from step import parse_original_ingredients

from typing import List, Tuple
from copy import deepcopy
from fuzzywuzzy import process
import spacy
nlp = spacy.load("en_core_web_sm")

from ingredient import Ingredient

def to_ingredients(sentences: List[str], ingredients:List[str]):
    matched_ingredients = []
    match_mappings=[]

    for sentence in sentences:
        sentence_match=[]
        doc = nlp(sentence.lower())
        current_mappings=[]
        # Extract noun phrases (potential ingredients)
        potential_ingredients = [token.text.strip() for token in doc if token.text.strip() and not token.is_stop]
        for potential in potential_ingredients:
            try:
                if str(potential).strip():
                    match, score = process.extractOne(str(potential), ingredients)
                    if score >= 80:
                        sentence_match.append(match)
                        current_mappings.append([str(potential),match])
            except TypeError:
                pass
        unique_matched_ingredients = list(set(sentence_match))
        matched_ingredients.append(unique_matched_ingredients)
        match_mappings.append(current_mappings)

    return matched_ingredients, match_mappings

def transform_healthy_or_vegan(recipe, transformation_type="healthy") -> Tuple[List[List[str]], List[Ingredient]]:
    # transform ingredients if it's unhealthy
    transformation_dict = transformations[transformation_type]
    new_ingredients_list = deepcopy(recipe.ingredients)
    for ingredient in new_ingredients_list:
        matching_ingredient = transform_ingredient(ingredient.name, transformation_dict)
        if matching_ingredient != ingredient.name:
            ingredient.update_name(matching_ingredient)
    
    # transform sentences if it includes unhealthy ingredients
    new_sentences_list = []
    for step in recipe.steps:
        ingredients_list, ingredients_mappings = to_ingredients(step.sentences, step.ingredients_names)
        transformed_ingredients = transform_ingredient_list(ingredients_list, transformation_type)
        new_sentences = transform_sentence_list(transformed_ingredients, ingredients_mappings, step.sentences, transformation_type)
        new_sentences_list.append(new_sentences)
    return new_sentences_list, new_ingredients_list

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