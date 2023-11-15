from typing import List, Union, Tuple
import re
import spacy
from fuzzywuzzy import process
nlp = spacy.load("en_core_web_sm")


from ingredient import Ingredient
from ingredient import parse_ingredients, get_ingredients_names

# TODO: modify types (using self-defined types)
DefineTemp = Tuple[str, str]
DefineIngrdnt = Ingredient
DefineTime = Tuple[float, float, str, int]
DefineMethod = str
DefineTool = str

TemperatureType = Union[DefineTemp, None]
IngredientsType = Union[List[DefineIngrdnt], None]
TimeType = Union[DefineTime, None]
MethodsType = Union[List[DefineMethod], None]
ToolsType = Union[List[DefineTool], None]
from web import get_soup_from_url, get_raw_ingredients_from_soup
from sentence_helper import celsius_to_fahren


# url = "https://www.allrecipes.com/recipe/217331/goan-pork-vindaloo/"
url = "https://www.allrecipes.com/recipe/12151/banana-cream-pie-i/"
soup, recipe_name = get_soup_from_url(url)
raw_ingredients = get_raw_ingredients_from_soup(soup)
ingredients = parse_ingredients(raw_ingredients)
ingredients_names = get_ingredients_names(ingredients)

def custom_tokenizer(nlp):
    infix_re = spacy.util.compile_infix_regex(nlp.Defaults.infixes + [r'(?<=[0-9])-'])
    return spacy.tokenizer.Tokenizer(nlp.vocab, infix_finditer=infix_re.finditer)

nlp.tokenizer = custom_tokenizer(nlp)

# TODO: will import these functions from other files
def to_temperature(sentences: List[str]) -> TemperatureType:
    temperatures=[]
    temperature=[]
    for sentence in sentences:
        tokens = sentence.split()  # Split the sentence into tokens
        # print("tokens: ", tokens)
        for i in range(len(tokens) - 1):
            token = tokens[i]
            next_token = tokens[i + 1]

            if token.isnumeric():
                if next_token.lower() in ["degrees", "degree", "°"]:
                    temperatures.append((token, tokens[i+2]))
            else:
                if (
                    token.lower() in ["low", "medium", "medium-high", "high"]
                    and  "heat" in next_token.lower()
                ):
                    temperatures.append((token, "heat"))

    print(temperatures)
    for temp, unit in temperatures:
        if unit.strip() in ["C","c","Celsius","celsius"]:
            converted_temp=celsius_to_fahren(float(temp))
            temperature=[str(converted_temp), "F"]
        elif unit.strip() in ["F","f","Fahrenheit","fahrenheit"]:
            temperature=[str(temp), "F"]
        else:
            temperature=[temp, unit]
    
    print("temperature: ", temperature)
    print("-------------")
    return tuple(temperature) if temperature else None

def to_ingredients(sentences: List[str], ingredients:List[str]) -> List[IngredientsType]:
    matched_ingredients = []
    for sentence in sentences:
        doc = nlp('You '+sentence.lower())
        # Extract noun phrases (potential ingredients)
        potential_ingredients = [chunk.text.strip() for chunk in doc.noun_chunks if chunk.text.strip()]

        for potential in potential_ingredients:
            try:
                if str(potential).strip():
                    match, score = process.extractOne(str(potential), ingredients)
                    if score >= 90:
                        matched_ingredients.append(match)
            except TypeError:
                pass

        unique_matched_ingredients = list(set(matched_ingredients))

    print("Unique Matched Ingredients:", unique_matched_ingredients)
    # print("#### ", sentences , "\n")
    print("---------")
    return [ [] for _ in sentences ]

def to_time(sentences: List[str]) -> List[TimeType]:
    times=[]
    for idx, sentence in enumerate(sentences):
        pattern = r'\b(\d+)(?:\D*?(?:to|-)\D*?(\d+))?\D*?(minutes?|mins?|hours?|hrs?|seconds?|secs?|days?)\b'
        matches = re.findall(pattern, sentence)
        print("matches: ", matches)
        if len(matches)>0:
            low, high=matches[0][0], matches[0][1]
            if len(matches[0][1])==0:
                high=matches[0][0]
            times.append((low,high, matches[0][2]))
        else:
            times.append(None)

    print("Extracted Time: ", times)
    print("----")
    return times

def to_method(sentences: List[str]) -> List[MethodsType]:
    return [ [] for _ in sentences ]

def to_tools(sentences: List[str]) -> List[ToolsType]:
    return [ [] for _ in sentences ]



def collect_tools(tools_list: List[ToolsType]) -> List[DefineTool]:
    """Collects all tools from a list of tools."""
    all_tools = []
    for tools in tools_list:
        if tools is not None:
            all_tools.extend(tools)
    return list(set(all_tools))

def collect_methods(method_list: List[MethodsType]) -> List[DefineMethod]:
    """Collects all methods from a list of methods."""
    all_methods = []
    for methods in method_list:
        if methods is not None:
            all_methods.extend(methods)
    return list(set(all_methods))

class Action:
    def __init__(self, sentence: str, temperature: TemperatureType, ingredients: IngredientsType, time: TimeType,
                 method: MethodsType, tools: ToolsType) -> None:
        self.sentence = sentence
        self.temperature = temperature
        self.ingredients = ingredients
        self.time = time
        self.method = method
        self.tools = tools

class Step:
    def __init__(self, sentences: List[str], ingredients:List[str]) -> None:
        self.actions: List[Action] = []
        
        temperature_value = to_temperature(sentences)
        ingredients_list = to_ingredients(sentences, ingredients_names)
        time_list = to_time(sentences)
        method_list = to_method(sentences)
        tools_list = to_tools(sentences)
        
        for i in range(len(sentences)):
            self.actions.append(Action(sentences[i], temperature_value, ingredients_list[i], time_list,
                                       method_list[i], tools_list[i]))
        self.tools = collect_tools(tools_list)
        self.methods = collect_methods(method_list)


def parse_steps(sentences_list: List[List[str]]) -> List[Step]:
    steps = []
    for sentences in sentences_list:
        steps.append(Step(sentences, ingredients_names))
    return steps    

def parse_tools(step_list: List[Step]) -> List[DefineTool]:
    tools_list = [step.tools for step in step_list]
    return collect_tools(tools_list)

def parse_methods(step_list: List[Step]) -> List[DefineMethod]:
    method_list = [step.methods for step in step_list]
    return collect_methods(method_list)
        