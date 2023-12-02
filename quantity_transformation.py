from typing import List, Tuple
from unicodedata import numeric
from fractions import Fraction
from word2num import Word2Num
import spacy
w2n = Word2Num(fuzzy_threshold=60)
spacy_model = spacy.load("en_core_web_lg")

from ingredient import Ingredient

# TODO: check quantity update ratio in the main transformation function
def transform_quantity(sentences_list: List[List[str]], ingredients_list: List[Ingredient], quantity_update_ratio: float) -> Tuple[List[List[str]], List[Ingredient]]:
    """Modify the quantity of ingredients in the sentences_list and ingredients_list by a ratio."""
    if quantity_update_ratio == 1.0:
        return sentences_list, ingredients_list
    elif quantity_update_ratio < 0.0:
        raise ValueError("quantity_update_ratio should be greater than 0.0")
    new_sentences_list = modify_quantity_sentences(sentences_list, quantity_update_ratio)
    new_ingredients_list = modify_quantity_ingredients(ingredients_list, quantity_update_ratio)
    return new_sentences_list, new_ingredients_list

# List[list[str]] -> List[list[str]]
def modify_quantity_sentences(sentences_list: List[List[str]], quantity_update_ratio: float) -> List[List[str]]:
    """Modify the quantity of ingredients in the sentences_list by a ratio."""
    new_sentences_list = []
    for sentences in sentences_list:
        new_sentences = []
        for sentence in sentences:
            new_sentences.append(modify_quantity_sentence(sentence, quantity_update_ratio))
        new_sentences_list.append(new_sentences)
    return new_sentences_list

# List[Ingredient] -> List[Ingredient]
def modify_quantity_ingredients(ingredients_list: List[Ingredient], quantity_update_ratio: float) -> List[Ingredient]:
    """Modify the quantity of ingredients in the ingredients_list by a ratio."""
    new_ingredients_list = []
    for ingredient in ingredients_list:
        new_ingredient = ingredient
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

def modify_quantity_sentence(sentence: str, quantity_update_ratio: float) -> str:
    """Modify the quantity of ingredients in the sentence by a ratio."""
    doc = spacy_model(sentence)
    new_sentence = sentence
    for token in doc:
        if token.pos_ == "NUM":
            new_quantity = parse_quantity(token.text) * quantity_update_ratio
            new_sentence = new_sentence.replace(token.text, quantity_to_str(new_quantity))
    return new_sentence