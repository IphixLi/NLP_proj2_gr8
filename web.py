import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import List, Tuple

def valid_url(url: str) -> bool:
    return "www.allrecipes.com/" in url

def get_soup_from_url(url: str) -> Tuple[BeautifulSoup, str]:
    """Returns a BeautifulSoup object and the website title from the given url. If error or the url is invalid, raise exception."""
    if not valid_url(url):
        raise Exception("Invalid url. url must contain 'www.allrecipes.com/'")
    
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        title = soup.find('title').get_text()
        return soup, title
    except Exception as e:
        raise Exception(f"Error when getting soup from url: {url}, error: {e}")

def get_raw_ingredients_from_soup(soup: BeautifulSoup) -> List[Tag]:
    """Returns a list of raw ingredients from the given soup. If not found, raise exception."""
    raw_ingredients = soup.select("#mntl-structured-ingredients_1-0 > ul > li > p")
    if not raw_ingredients:
        raise Exception("No ingredients found.")
    return raw_ingredients

def get_raw_steps_from_soup(soup: BeautifulSoup) -> List[Tag]:
    """Returns a list of raw steps from the given soup. If not found, raise exception."""
    raw_steps = soup.select("#mntl-sc-block_2-0 > li > p")
    if not raw_steps:
        raise Exception("No steps found.")
    return raw_steps

if __name__ == "__main__":
    url = "https://www.allrecipes.com/recipe/12151/banana-cream-pie-i/"
    soup, title=get_soup_from_url(url)
    res=get_raw_ingredients_from_soup(soup)
    for val in res:
        print(val.get_text().strip())
        print()