from typing import List
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

