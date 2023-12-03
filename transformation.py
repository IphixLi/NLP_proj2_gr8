from fuzzywuzzy import fuzz
from transformationDB import transformations
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

def transform_ingredient_list(ingredient_list, transformation_type):
    transformation_dict=transformations[transformation_type]
    new_ingredients=[]
    for step in ingredient_list:
        new_step=[]
        for ingredient in step:
            # find matching ingredient in transformations
            matching_ingredient = transform_ingredient(ingredient,transformation_dict)
            if matching_ingredient!=ingredient:
                new_step.append([ingredient, matching_ingredient])
            else:
                new_step.append([ingredient, ingredient])
        new_ingredients.append(new_step)
    return new_ingredients

def transform_ingredient(ingredient, transformation_dict):
    matching_ingredient = find_closest_match(ingredient, transformation_dict)
    if matching_ingredient:
        return matching_ingredient
    else:
        return ingredient

# transformation for sentence list
def transform_sentence_list(modified_ingredient_list, ingredient_mappings, sentence_list, transformation_type):
    transformation_dict=transformations[transformation_type]
    new_sentence_list=[]
    for idx, sentence in enumerate(sentence_list):
        for i, ingr in enumerate(ingredient_mappings[idx]):
            from_official_name=transform_ingredient(ingr[1], transformation_dict )
            if from_official_name!=ingr[1]:
                sentence=sentence.replace(ingr[0],from_official_name)
            else:
                from_raw_name=transform_ingredient(ingr[0], transformation_dict)
                sentence=sentence.replace(ingr[0], from_raw_name)
        new_sentence_list.append(sentence)
    
    print("new: ", new_sentence_list, sentence_list)
    return new_sentence_list
        

def find_closest_match(input_key, substitution_list):
    closest_match, match_val= max(substitution_list.items(), key=lambda x: fuzz.ratio(x[0], input_key))
    
    # You can adjust the threshold based on your preferences\
    similarity=fuzz.ratio(closest_match, input_key)
    # print("test??", input_key, ",", closest_match,",", match_val, similarity )
    if similarity > 70:
        return match_val
    else:
        return None


# given list of sentences replace words in sentences with the ones near them for example 
# [[['flour tortillas', 'lettuce leaves'], ['deli ham', 'deli ham']], [['flour tortillas', 'lettuce leaves'], ['olby-Jack cheese', 'olby-Jack cheese']], [['flour tortillas', 'lettuce leaves']], []]
# ingredient_list:  [[]]

# so where there is 