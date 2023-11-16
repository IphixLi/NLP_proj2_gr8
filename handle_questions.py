from typing import List

from ToActionFuctions import answerVague
from step import IngredientsType, ToolsType

def is_specific_question(sentence: str) -> bool:
    """Returns True if the sentence is a specific question.
    
    Possible formats:
    - (what is|how to) [some specific content]: specific
    """
    if sentence.startswith("what is ") or sentence.startswith("how to "):
        return True
    else:
        return False

def is_vague_question(sentence: str) -> bool:
    """Returns True if the sentence is a vague question.
    
    Possible formats:
    - vague (what|how): vague
    """
    if sentence in ["vague what", "vague how"]:
        return True
    else:
        return False

def is_question(sentence: str) -> bool:
    """Returns True if the sentence is a question.
    
    Possible formats:
    - (what is|how to) [some specific content]: specific
    - vague (what|how): vague
    """
    if sentence.startswith("what is ") or sentence.startswith("how to "):
        return True
    elif sentence in ["vague what", "vague how"]:
        return True
    else:
        return False      

def build_url_from_question(question: str, use_google: bool) -> str:
    """
    Builds a URL from a question.
    
    Example: 
    - "how to preheat oven" + use_google -> "https://www.google.com/search?q=how+to+preheat+oven"
    - "how to preheat oven" + not use_google -> "https://www.youtube.com/results?search_query=how+to+preheat+oven"
    """
    if use_google:
        return "https://www.google.com/search?q=" + "+".join(question.split())
    else:
        return "https://www.youtube.com/results?search_query=" + "+".join(question.split())

def handle_specific_question(question: str) -> None:
    print()
    print(f"Question: {question}")
    print("-------------------")
    print(f"- answers from google: {build_url_from_question(question, use_google=True)}")
    print(f"- answers from youtube: {build_url_from_question(question, use_google=False)}")
    
    
def handle_fuzzy_what_questions(ingredients_names: IngredientsType, tools: ToolsType) -> None:
    if ingredients_names is not None and len(ingredients_names) > 0:
        print()
        print("Questions you might ask about ingredients used here: ")
        print("-------------------")
        for ingredient in ingredients_names:
            print(f"{ingredient}: {build_url_from_question(f'what is {ingredient}', use_google=True)}")
    
    if tools is not None and len(tools) > 0:
        print()
        print("Questions you might ask about tools used here: ")
        print("-------------------")
        for tool in tools:
            print(f"{tool}: {build_url_from_question(f'what is {tool}', use_google=True)}")


def handle_fuzzy_how_questions(sentence: str) -> None:
    actions_list = answerVague(sentence)
    
    if len(actions_list) > 0:
        print()
        print("- Questions you might ask about actions in this step: ")
        print("-------------------")
        for action in actions_list:
            print(f"{action}: {build_url_from_question(f'how to use {action}', use_google=True)}")