from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import List, Tuple
from unicodedata import numeric

class Ingredient:
    def __init__(self, ingredient: Tag) -> None:
        self.quantity = self.extract_quantity(ingredient)
        self.unit = self.extract_unit(ingredient)
        self.name, self.preparation = self.extract_name_preparation(ingredient)
        
    def extract_quantity(self, ingredient: Tag) -> float:
        quantity_text = ingredient.find("span", {"data-ingredient-quantity": "true"}).text
        quantity = 0.0
        
        for quantity_part in quantity_text.split():
            try:
                quantity += float(quantity_part)
            except ValueError:
                quantity += numeric(quantity_part)
        return quantity
    
    def extract_unit(self, ingredient: Tag) -> str:
        return ingredient.find("span", {"data-ingredient-unit": "true"}).text
    
    def extract_name_preparation(self, ingredient: Tag) -> Tuple[str, str]:
        name_text = ingredient.find("span", {"data-ingredient-name": "true"}).text
        if ", " in name_text:
            return tuple(name_text.split(", ", 1))
        else:
            return name_text, ""
    
    def __str__(self) -> str:
        return f"quantity: {self.quantity}, unit: {self.unit}, name: {self.name}, preparation: {self.preparation}"


def parse_ingredients(soup: BeautifulSoup) -> List[Ingredient]:
    ingredients = []
    
    for ingredient in soup.select("#mntl-structured-ingredients_1-0 > ul > li > p"):
        ingredients.append(Ingredient(ingredient))
        
    return ingredients