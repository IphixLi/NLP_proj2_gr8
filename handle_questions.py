from typing import List

def build_url_from_question(question: str, use_google: bool) -> str:
    """
    Builds a URL from a question.
    
    Example: "how to preheat oven" + use_google -> "https://www.google.com/search?q=how+to+preheat+oven"
             "how to preheat oven" + not use_google -> "https://www.youtube.com/results?search_query=how+to+preheat+oven"
    """
    if use_google:
        return "https://www.google.com/search?q=" + "+".join(question.split())
    else:
        return "https://www.youtube.com/results?search_query=" + "+".join(question.split())

def handle_specific_question(question: str) -> None:
    print(f"Question: {question}")
    print(f"- answers from google: {build_url_from_question(question, use_google=True)}")
    print(f"- answers from youtube: {build_url_from_question(question, use_google=False)}")
    print()
    
def handle_fuzzy_what_questions(ingredients_names: List[str], tools: List[str]) -> None:
    print("- Questions you might ask about ingredients used here: ")
    for ingredient in ingredients_names:
        print(f"{ingredient}: {build_url_from_question(f'what is {ingredient}', use_google=True)}")
    
    print()
    print("- Questions you might ask about tools used here: ")
    for tool in tools:
        print(f"{tool}: {build_url_from_question(f'what is {tool}', use_google=True)}")
    print()
    print()