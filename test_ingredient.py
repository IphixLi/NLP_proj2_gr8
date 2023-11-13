from ingredient import parse_ingredients
from web import get_soup_from_url, get_raw_ingredients_from_soup

def main():
    # url = "https://www.allrecipes.com/air-fryer-ham-and-cheese-wraps-recipe-8365118"
    
    # problem 1: 1 (15 ounce) can kidney beans, drained (put "1 ( 15" into quantity)
    # problem 2: salt and freshly ground black pepper to taste (no quantity or unit)
    url = "https://www.allrecipes.com/easy-5-ingredient-chili-recipe-7508143"   
    
    # normal
    # url = "https://www.allrecipes.com/recipe/277720/buttermilk-pumpkin-pancakes/"
    
    # url = "https://www.allrecipes.com/recipe/222979/chicken-milanese/"
    
    
    url = "https://www.allrecipes.com/recipe/228823/quick-beef-stir-fry/"
    
    soup, _ = get_soup_from_url(url)
    raw_ingredients = get_raw_ingredients_from_soup(soup)
    ingredients = parse_ingredients(raw_ingredients)
    for ingredient in ingredients:
        print(repr(ingredient))

if __name__ == "__main__":
    main()