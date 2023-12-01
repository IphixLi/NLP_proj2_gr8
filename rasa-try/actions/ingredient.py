from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import List, Tuple
from unicodedata import numeric
from fractions import Fraction
from fuzzywuzzy import fuzz

class Ingredient:
    def __init__(self, ingredient: Tag) -> None:
        self.string = ingredient.text
        self.quantity, remaining_str = self.extract_quantity(ingredient)
        self.remaining_quantity=self.quantity
        self.unit = self.extract_unit(ingredient, remaining_str)
        self.name, self.preparation = self.extract_name_preparation(ingredient)
    
    def is_same_ingredient(self, other_ingredient: str) -> bool:
        # if similarity score is high enough, return True
        # or if one contains the other, return True
        if fuzz.ratio(self.name, other_ingredient) > 80:
            return True
        if self.name in other_ingredient or other_ingredient in self.name:
            return True
        else:
            return False

    def update_remaining_quantity(self,new_quantity: float) -> None:
        self.remaining_quantity=new_quantity

    def update_unit(self,new_unit: str) -> None:
        self.unit=new_unit

    def update_name(self,new_name: str) -> None:
        self.name=new_name

    def update_preparation(self,new_preparation: str) -> None:
        self.preparation=new_preparation       
        
    def extract_quantity(self, ingredient: Tag) -> Tuple[float, str]:
        quantity_tag = ingredient.find("span", {"data-ingredient-quantity": "true"})
        if quantity_tag is None:
            return 0.0, ""
        
        quantity_text = quantity_tag.text
        quantity = 0.0
        
        for quantity_part in quantity_text.split():
            if quantity_part.startswith("(") or quantity_part.startswith("["):
                return quantity, f"({quantity_text.split(' (')[1]}"
            try:
                quantity += float(quantity_part)
                continue
            except ValueError:
                pass
            
            try:
                quantity += float(Fraction(quantity_part))
                continue
            except ValueError:
                pass
            
            try:
                quantity += numeric(quantity_part)
                continue
            except TypeError:
                pass
            
            print(f"Error in extract quantity for ingredients: fail to convert {quantity_part} to float or fraction")
        return quantity, ""
    
    def extract_unit(self, ingredient: Tag, remaining_str: str) -> str:
        unit_tag = ingredient.find("span", {"data-ingredient-unit": "true"})
        if unit_tag is None:
            return remaining_str
        else:
            if remaining_str:
                return remaining_str + " " + unit_tag.text
            else:
                return unit_tag.text
    
    def extract_name_preparation(self, ingredient: Tag) -> Tuple[str, str]:
        name_text = ingredient.find("span", {"data-ingredient-name": "true"}).text
        if ", " in name_text:
            return tuple(name_text.split(", ", 1))
        else:
            return name_text, ""

    def __repr__(self) -> str:
        return f"quantity: {self.quantity}, unit: {self.unit}, name: {self.name}, preparation: {self.preparation}"
    
    def __str__(self) -> str:
        return self.string


def parse_ingredients(raw_ingredients: List[Tag]) -> List[Ingredient]:
    ingredients = []
    
    for ingredient in raw_ingredients:
        ingredients.append(Ingredient(ingredient))
        
    return ingredients

def get_ingredients_names(ingredients:List[Ingredient]) -> List[str]:
    return [ingredient.name for ingredient in ingredients]
    