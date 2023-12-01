from typing import List

from .ToActionFuctions import answerVague
from .step import IngredientsType, ToolsType

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

# handle specific question, except return a string instead of printing
def handle_specific_question_string(question: str) -> str:
    msg = ""
    msg += f"\nQuestion: {question}"
    msg += "\n-------------------"
    msg += f"\n- answers from google: {build_url_from_question(question, use_google=True)}"
    msg += f"\n- answers from youtube: {build_url_from_question(question, use_google=False)}"
    return msg
    
    
def handle_fuzzy_what_questions(ingredients_names: IngredientsType, tools: ToolsType) -> None:
    if ingredients_names is not None and len(ingredients_names) > 0:
        print()
        print("Questions you might ask about ingredients used here: ")
        print("-------------------")
        for ingredient in ingredients_names:
            print(f"{ingredient}: {build_url_from_question(f'what is {ingredient}', use_google=True)}")
        print()
    
    if tools is not None and len(tools) > 0:
        print()
        print("Questions you might ask about tools used here: ")
        print("-------------------")
        for tool in tools:
            print(f"{tool}: {build_url_from_question(f'what is {tool}', use_google=True)}")

# handle fuzzy what questions, except return a string instead of printing
def handle_fuzzy_what_questions_string(ingredients_names: IngredientsType, tools: ToolsType) -> str:
    msg = ""
    if ingredients_names is not None and len(ingredients_names) > 0:
        msg += "\nQuestions you might ask about ingredients used here: "
        msg += "\n-------------------"
        for ingredient in ingredients_names:
            msg += f"\n{ingredient}: {build_url_from_question(f'what is {ingredient}', use_google=True)}"
        msg += "\n"
    
    if tools is not None and len(tools) > 0:
        msg += "\nQuestions you might ask about tools used here: "
        msg += "\n-------------------"
        for tool in tools:
            msg += f"\n{tool}: {build_url_from_question(f'what is {tool}', use_google=True)}"
    return msg


def handle_fuzzy_how_questions(sentence: str) -> None:
    actions_list = answerVague(sentence)
    
    if len(actions_list) > 0:
        print()
        print("- Questions you might ask about actions in this step: ")
        print("-------------------")
        for action in actions_list:
            print(f"{action}: {build_url_from_question(f'how to {action}', use_google=True)}")

# handle fuzzy how questions, except return a string instead of printing
def handle_fuzzy_how_questions_string(sentence: str) -> str:
    msg = ""
    actions_list = answerVague(sentence)
    
    if len(actions_list) > 0:
        msg += "\n- Questions you might ask about actions in this step: "
        msg += "\n-------------------"
        for action in actions_list:
            msg += f"\n{action}: {build_url_from_question(f'how to {action}', use_google=True)}"
    return msg