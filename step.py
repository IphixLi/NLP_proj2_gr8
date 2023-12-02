from typing import List, Union, Tuple, Dict
import re
import spacy
from fuzzywuzzy import process
nlp = spacy.load("en_core_web_sm")
spacy_model = spacy.load("en_core_web_lg")


from ingredient import Ingredient
from ToActionFuctions import findTool, findMethod
from sentence_helper import imperative_to_normal
from spacy_helper import find_ingredient_index, find_num_index_list

# TODO: modify types (using self-defined types)
DefineTemp = Tuple[str, str] # (temperature, unit)
DefineIngrdnt = str
DefineTime = Tuple[float, float, str]   # (lower, higher, unit)
DefineMethod = str
DefineTool = str

TemperatureType = Union[DefineTemp, None]
IngredientsType = Union[List[DefineIngrdnt], None]
TimeType = Union[DefineTime, None]
MethodsType = Union[List[DefineMethod], None]
ToolsType = Union[List[DefineTool], None]
from sentence_helper import celsius_to_fahren


def custom_tokenizer(nlp):
    infix_re = spacy.util.compile_infix_regex(nlp.Defaults.infixes + [r'(?<=[0-9])-'])
    return spacy.tokenizer.Tokenizer(nlp.vocab, infix_finditer=infix_re.finditer)

# tokenizer that ignore "-" character

nlp.tokenizer = custom_tokenizer(nlp)

# TODO: will import these functions from other files
def to_temperature(sentences: List[str]) -> TemperatureType:
    temperatures=[]
    temperature=[]
    for sentence in sentences:
        tokens = sentence.split()  # Split the sentence into tokens
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

    for temp, unit in temperatures:
        if unit.strip() in ["C","c","Celsius","celsius"]:
            converted_temp=celsius_to_fahren(float(temp))
            temperature=[str(converted_temp), "F"]
        elif unit.strip() in ["F","f","Fahrenheit","fahrenheit"]:
            temperature=[str(temp), "F"]
        else:
            temperature=[temp, unit]
    return tuple(temperature) if temperature else None

def temperature_to_str(temperature: TemperatureType) -> str:
    """Converts a temperature tuple to a string.
    - temperature is None: ""
    - temperature is not None: "temp degrees unit"
    """
    if temperature is None:
        return ""
    else:
        temp, unit = temperature
        return f"{temp} degrees {unit}"

def to_ingredients(sentences: List[str], ingredients:List[str]) -> List[IngredientsType]:
    matched_ingredients = []

    for sentence in sentences:
        sentence_match=[]
        doc = nlp(sentence.lower())
        # Extract noun phrases (potential ingredients)
        potential_ingredients = [chunk.text.strip() for chunk in doc if chunk.text.strip()]
        for potential in potential_ingredients:
            try:
                if str(potential).strip():
                    match, score = process.extractOne(str(potential), ingredients)
                    if score >= 80:
                        sentence_match.append(match)
            except TypeError:
                pass
        unique_matched_ingredients = list(set(sentence_match))
        matched_ingredients.append(unique_matched_ingredients)

    print("ingr: ", matched_ingredients)
    print(sentences)
    print("---------------")
    return matched_ingredients

def to_time(sentences: List[str]) -> List[TimeType]:
    times=[]
    for idx, sentence in enumerate(sentences):
        pattern = r'\b(\d+)(?:\D*?(?:to|-)\D*?(\d+))?\D*?(minutes?|mins?|hours?|hrs?|seconds?|secs?|days?)\b'
        matches = re.findall(pattern, sentence)
        if len(matches)>0:
            low, high=matches[0][0], matches[0][1]
            if len(matches[0][1])==0:
                high=matches[0][0]
            times.append((low,high, matches[0][2]))
        else:
            times.append(None)

    return times

def time_to_str(time: TimeType) -> str:
    """Converts a time tuple to a string.
    - time is None: ""
    - low == high: "low unit"
    - low != high: "low to high unit"
    """
    if time is None:
        return ""
    else:
        low, high, unit = time
        if low == high:
            return f"{low} {unit}"
        else:
            return f"{low} to {high} {unit}"

def to_method(sentences: List[str]) -> List[MethodsType]:
    return findMethod(sentences)

def to_tools(sentences: List[str]) -> List[ToolsType]:
    return findTool(sentences)



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
        self.ingredients_info = self.find_all_ingredients_info(ingredients)   # dictionary of (ingredient, info_str) pairs
    
    def get_time_str(self) -> str:
        return time_to_str(self.time)
    
    def get_temperature_str(self) -> str:
        return temperature_to_str(self.temperature)
    
    def get_ingredients_info_str(self, ingredient_name: str) -> str:
        # requires: ingredient_name should be spelled correctly
        return self.ingredients_info.get(ingredient_name, "")

    def find_all_ingredients_info(self, ingredient_names: List[str]) -> Dict[str, str]:
        """Return a dictionary of (ingredient, info_str) pairs."""
        imperative_sentence = imperative_to_normal(self.sentence)
        doc = spacy_model(imperative_sentence)
        
        # try to find all the ingredients index in the sentence
        ingredients_index_dict = {}
        for i in ingredient_names:
            i_index = find_ingredient_index(doc, i)
            if i_index != -1:
                ingredients_index_dict[i] = i_index
        
        if len(ingredients_index_dict) == 0:
            return {}
        
        # num_index_list is ascending order
        num_index_list = find_num_index_list(doc)
        if len(num_index_list) == 0:
            return {}

        # also in ascending order [(ingredient, index)]
        sorted_i_index_list = sorted(ingredients_index_dict.items(), key=lambda item: item[1])
        
        # move two pointers to find (num, ingredient) pair (num_index < i_index and num_index is the closest, num_index is used once)
        i_ptr = 0
        num_ptr = 0
        result_dict = {}
        while i_ptr < len(sorted_i_index_list) and num_ptr < len(num_index_list):
            i_index = sorted_i_index_list[i_ptr][1]
            num_index = num_index_list[num_ptr]
            
            if i_index < num_index:
                i_ptr += 1
            else:
                info_str = doc[num_index:i_index+1].text
                result_dict[sorted_i_index_list[i_ptr][0]] = info_str
                num_ptr += 1
        return result_dict
        

class Step:
    def __init__(self, sentences: List[str], ingredients_names: List[str]) -> None:
        self.actions: List[Action] = []
        
        temperature_value = to_temperature(sentences)
        ingredients_list = to_ingredients(sentences, ingredients_names)
        time_list = to_time(sentences)
        method_list = to_method(sentences)
        tools_list = to_tools(sentences)

        for i in range(len(sentences)):
            print("res: ", sentences[i],temperature_value,ingredients_list[i],time_list[i],method_list[i],tools_list[i])
            self.actions.append(Action(sentences[i], temperature_value, ingredients_list[i], time_list[i],
                                       method_list[i], tools_list[i]))
        self.tools = collect_tools(tools_list)
        self.methods = collect_methods(method_list)


def parse_steps(sentences_list: List[List[str]], ingredients_names: List[str]) -> List[Step]:
    steps = []
    for sentences in sentences_list:
        step=Step(sentences, ingredients_names)
        steps.append(step)
    return steps    

def parse_tools(step_list: List[Step]) -> List[DefineTool]:
    tools_list = [step.tools for step in step_list]
    return collect_tools(tools_list)

def parse_methods(step_list: List[Step]) -> List[DefineMethod]:
    method_list = [step.methods for step in step_list]
    return collect_methods(method_list)
        