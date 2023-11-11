import requests
from bs4 import BeautifulSoup
from typing import List

def split_into_sentences(text: str) -> List[str]:
    return text.strip().replace(";", ".").split(". ")

def add_punctuation(sentence: str) -> str:
    if sentence[-1] not in ".!?":
        return sentence + "."
    else:
        return sentence

def get_steps_from_url(url: str) -> List[List[str]]:
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    steps = []
    
    for step in soup.select("#mntl-sc-block_2-0 > li > p"):
        step_sentences = split_into_sentences(step.text)
        steps.append([add_punctuation(sentence) for sentence in step_sentences])
    
    return steps

if __name__ == "__main__":
    url = "https://www.allrecipes.com/recipe/12151/banana-cream-pie-i/"
    print(get_steps_from_url(url))