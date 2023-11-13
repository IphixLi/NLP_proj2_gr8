from typing import List, Union

from ingredient import Ingredient

# TODO: modify types (using self-defined types)
DefineTemp = int
DefineIngrdnt = Ingredient
DefineTime = int
DefineMethod = str
DefineTool = str

TemperatureType = Union[DefineTemp, None]
IngredientsType = Union[List[DefineIngrdnt], None]
TimeType = Union[DefineTime, None]
MethodsType = Union[List[DefineMethod], None]
ToolsType = Union[List[DefineTool], None]


# TODO: will import these functions from other files
def to_temperature(sentences: List[str]) -> List[TemperatureType]:
    return [ [] for _ in sentences ]

def to_ingredients(sentences: List[str]) -> List[IngredientsType]:
    return [ [] for _ in sentences ]

def to_time(sentences: List[str]) -> List[TimeType]:
    return [ [] for _ in sentences ]

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
    def __init__(self, sentences: List[str]) -> None:
        self.actions: List[Action] = []
        
        temperature_list = to_temperature(sentences)
        ingredients_list = to_ingredients(sentences)
        time_list = to_time(sentences)
        method_list = to_method(sentences)
        tools_list = to_tools(sentences)
        
        for i in range(len(sentences)):
            self.actions.append(Action(sentences[i], temperature_list[i], ingredients_list[i], time_list[i],
                                       method_list[i], tools_list[i]))
        self.tools = collect_tools(tools_list)
        self.methods = collect_methods(method_list)


def parse_steps(sentences_list: List[List[str]]) -> List[Step]:
    steps = []
    for sentences in sentences_list:
        steps.append(Step(sentences))
    return steps    

def parse_tools(step_list: List[Step]) -> List[DefineTool]:
    tools_list = [step.tools for step in step_list]
    return collect_tools(tools_list)

def parse_methods(step_list: List[Step]) -> List[DefineMethod]:
    method_list = [step.methods for step in step_list]
    return collect_methods(method_list)
        
    