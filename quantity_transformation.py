from typing import List, Tuple
from unicodedata import numeric
from fractions import Fraction
from word2num import Word2Num
from copy import deepcopy
import spacy
w2n = Word2Num(fuzzy_threshold=60)
spacy_model = spacy.load("en_core_web_lg")

from ingredient import Ingredient
from step import Action, Step
from sentence_helper import imperative_to_normal

# option 2: def transform_quantity(sentences_list: List[List[str]], ingredients_list: List[Ingredient], quantity_update_ratio: float) -> Tuple[List[List[str]], List[Ingredient]]:
def transform_quantity(recipe, quantity_update_ratio: float) -> Tuple[List[List[str]], List[Ingredient]]:
    """Modify the quantity of ingredients in the sentences_list and ingredients_list by a ratio."""
    sentences_list = deepcopy(recipe.sentences_list)  # List[List[str]]
    ingredients_list = deepcopy(recipe.ingredients)  # List[Ingredient]
    
    if quantity_update_ratio == 1.0:
        return sentences_list, ingredients_list
    elif quantity_update_ratio < 0.0:
        raise ValueError("quantity_update_ratio should be greater than 0.0")
    new_sentences_list = modify_quantity_steps(recipe.steps, quantity_update_ratio)
    new_ingredients_list = modify_quantity_ingredients(ingredients_list, quantity_update_ratio)
    return new_sentences_list, new_ingredients_list


# List[list[str]] -> List[list[str]]
def modify_quantity_steps(step_list: List[Step], quantity_update_ratio: float) -> List[List[str]]:
    """Modify the quantity of ingredients in the sentences_list by a ratio."""
    new_sentences_list = []
    for step in step_list:
        new_sentences = []
        for action in step.actions:
            new_sentences.append(modify_quantity_action(action, quantity_update_ratio))
        new_sentences_list.append(new_sentences)
    return new_sentences_list

def modify_quantity_action(action: Action, quantity_update_ratio: float) -> str:
    """Modify the quantity of ingredients in the sentence by a ratio (only update numbers related to ingredients)."""
    if "each" in action.sentence:
        return action.sentence
    
    doc = spacy_model(imperative_to_normal(action.sentence))
    new_sentence = action.sentence
    ingredients_info_list = list(action.ingredients_info.values()) # List of (info_str, num_index, i_index)
    
    if len(ingredients_info_list) == 0:
        return new_sentence
    
    cur_info_idx = 0
    token_index = 0
    while token_index < len(doc) and cur_info_idx < len(ingredients_info_list):
        if doc[token_index].pos_ != "NUM":
            token_index += 1
            continue
        info_str, num_index, i_index = ingredients_info_list[cur_info_idx]
        if token_index < num_index:
            token_index += 1
            continue
        elif token_index > i_index:
            cur_info_idx += 1
            continue
        else:
            # check if there is a sequence of number tokens
            token_index_end = token_index + 1
            while token_index_end < len(doc) and doc[token_index_end].pos_ == "NUM":
                token_index_end += 1
            # parse quantity and update
            quantity_str = doc[token_index:token_index_end].text
            new_quantity = parse_quantity(quantity_str) * quantity_update_ratio
            # print(f"quantity_str: {quantity_str}, new_quantity: {new_quantity}, quantity_update_ratio: {quantity_update_ratio}")
            new_quantity_str = quantity_to_str(new_quantity)
            new_info_str = info_str.replace(quantity_str, new_quantity_str)
            new_sentence = new_sentence.replace(info_str, new_info_str)
            # move to next token
            token_index = token_index_end + 1
    return new_sentence

# List[Ingredient] -> List[Ingredient]
def modify_quantity_ingredients(ingredients_list: List[Ingredient], quantity_update_ratio: float) -> List[Ingredient]:
    """Modify the quantity of ingredients in the ingredients_list by a ratio."""
    new_ingredients_list = []
    for ingredient in ingredients_list:
        new_ingredient = deepcopy(ingredient)
        new_ingredient.update_remaining_quantity(ingredient.remaining_quantity * quantity_update_ratio)
        new_ingredients_list.append(new_ingredient)
    return new_ingredients_list

def parse_quantity(quantity_str: str) -> float:
    """Parse the quantity string into a float."""
    if quantity_str == "":
        return 0.0
    
    # case: one
    try:
        result = w2n.parse(quantity_str)
        if result:
            return result
    except Exception:
        pass
    if " " in quantity_str:
        quantity_str = quantity_str.split()[0]
    # case: 1.03
    try:
        return float(quantity_str)
    except ValueError:
        pass
    # case: 1/2
    try:
        return float(Fraction(quantity_str))
    except ValueError:
        pass
    # case: ½
    try:
        return numeric(quantity_str)
    except ValueError:
        pass
    return 0.0

def quantity_to_str(quantity: float) -> str:
    if quantity.is_integer():
        return str(int(quantity))
    else:
        return str(quantity)
