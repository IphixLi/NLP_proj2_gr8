from typing import List, Union
from bs4.element import Tag


def split_into_sentences(text: str) -> List[str]:
    return text.strip().replace(";", ".").split(". ")

def add_punctuation(sentence: str) -> str:
    if sentence[-1] not in ".!?":
        return sentence + "."
    else:
        return sentence
    
def imperative_to_normal(sentence: str) -> str:
    if sentence.endswith("."):
        return f"You {sentence[0].lower()}{sentence[1:]}"
    else:
        return f"You {sentence[0].lower()}{sentence[1:]}."

def raw_steps_to_list_sentences(raw_steps: List[Tag]) -> List[List[str]]:
    sentences_list = []
    for step in raw_steps:
        step_sentences = split_into_sentences(step.text)
        sentences_list.append([add_punctuation(sentence) for sentence in step_sentences])
    return sentences_list

def celsius_to_fahren(temperature:float)->Union[float, None]:
    try:
        convert_to_celsius=(float(temperature)*9/5)+32
    except:
        return None
    return convert_to_celsius

