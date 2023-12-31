from enum import Enum
from typing import Callable

from .recipe import Recipe
from .handle_questions import handle_specific_question_string, handle_fuzzy_what_questions_string, handle_fuzzy_how_questions_string

class RasaState(Enum):
    QUIT = -1
    RESTART = 0
    INPUT_URL = 1
    ABSTRACT = 2
    ACTION = 3
    FINISH = 4
    
# singleton class used by rasa actions
class RecipeRasaStateMachine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.reset()
        return cls._instance
    
    def reset(self) -> None:
        self.state = RasaState.INPUT_URL
        self.recipe = None
        self.current_action = 0
        self.start_instructions = False
        self.url = ""
    
    def set_url(self, url: str) -> None:
        self.url = url
    
    def set_state(self, state: RasaState) -> None:
        self.state = state
    
    def set_action(self, action: int) -> None:
        # [0, num_actions)
        if action < 0 or action >= self.recipe.num_actions:
            raise Exception("")
        self.current_action = action
    
    def check_recipe(self) -> None:
        if self.recipe is None:
            raise Exception("No recipe loaded. Please provide a recipe url first.")
    
    
    def parse_recipe(self) -> str:
        try:
            self.recipe = Recipe(self.url)
            return f"Successfully parsed recipe {self.recipe.recipe_name}."
        except Exception as e:
            raise Exception(f"Error while fetching the recipe: {e}. Please try again.")
    
    def get_abstract_msg(self) -> str:
        # check if recipe is loaded
        self.check_recipe()
        
        msg = "\nRecipe Overview:\n"
        msg += "-------------------\n"
        msg += self.recipe.get_abstract()
        return msg
    
    def get_ingredients_msg(self) -> str:
        # check if recipe is loaded
        self.check_recipe()
        
        msg = "\nRecipe Ingredients:\n"
        msg += "-------------------\n"
        msg += self.recipe.get_ingredients()
        return msg
    
    def get_all_actions_msg(self) -> str:
        # check if recipe is loaded
        self.check_recipe()
        
        msg = "\nRecipe Steps:\n"
        msg += "-------------------\n"
        msg += self.recipe.get_all_actions()
        return msg
    
    def next_step(self) -> str:
        # check if recipe is loaded
        self.check_recipe()
        
        try:
            if self.start_instructions:
                self.set_action(self.current_action + 1)
            else:
                self.start_instructions = True
            msg = f"Step {self.current_action + 1} / {self.recipe.num_actions} of the recipe:"
            msg += "\n-------------------\n"
            msg += self.recipe.get_action_info(self.current_action)
            return msg
        except:
            return "You've reached the end of the recipe. Enjoy your meal!"
    
    def prev_step(self) -> str:
        # check if recipe is loaded
        self.check_recipe()
        
        try:
            self.set_action(self.current_action - 1)
            msg = f"Step {self.current_action + 1} / {self.recipe.num_actions} of the recipe:"
            msg += "\n-------------------\n"
            msg += self.recipe.get_action_info(self.current_action)
            self.start_instructions = True
            return msg
        except:
            return "You've reached the beginning of the recipe."
    
    def repeat_step(self) -> str:
        # check if recipe is loaded
        self.check_recipe()
        
        self.start_instructions = True
        msg = f"Step {self.current_action + 1} / {self.recipe.num_actions} of the recipe:"
        msg += "\n-------------------\n"
        msg += self.recipe.get_action_info(self.current_action)
        return msg

    def restart_instructions(self) -> str:
        # check if recipe is loaded
        self.check_recipe()
        
        self.start_instructions = True
        self.set_action(0)
        msg = f"Step {self.current_action + 1} / {self.recipe.num_actions} of the recipe:"
        msg += "\n-------------------\n"
        msg += self.recipe.get_action_info(self.current_action)
        return msg
    
    def jump_to_step(self, step: int) -> str:
        # check if recipe is loaded
        self.check_recipe()
        
        try:
            self.set_action(step - 1)
            self.start_instructions = True
            msg = f"Step {self.current_action + 1} / {self.recipe.num_actions} of the recipe:"
            msg += "\n-------------------\n"
            msg += self.recipe.get_action_info(self.current_action)
            return msg
        except Exception as e:
            print(e)
            raise Exception(f"Invalid step number: {step}. Please enter a number between 1 and {self.recipe.num_actions}.")
    
    def ask_step_parameter(self, question: str, ingredient_name = "") -> str:
        # check if recipe is loaded
        self.check_recipe()
        
        action = self.recipe.get_action(self.current_action)
        question = question.lower() + " "
        
        msg = ""
        if "how long" in question or "when" in question:
            msg += "Fetching time information...\n"
            time_str = action.get_time_str()
            if time_str:
                msg += f"This step takes {time_str}.\n"
            else:
                msg += "Sorry, I can't find the time information for this step.\n"
        elif "temperature" in question:
            msg += "Fetching temperature information...\n"
            temperature_str = action.get_temperature_str()
            if temperature_str:
                msg += f"The temperature for this step is {temperature_str}.\n"
            else:
                msg += "Sorry, I can't find the temperature information for this step.\n"
        elif ingredient_name or "how much " in question or "how many " in question:
            msg += "Fetching ingredient information...\n"
            if not ingredient_name:
                if "how much" in question:
                    ingredient_name = question.split("how much ")[1]
                else:
                    ingredient_name = question.split("how many ")[1]
                if " of " in ingredient_name:
                    ingredient_name = ingredient_name.split(" of ")[0] + " " + ingredient_name.split(" of ")[1]
                possible_trailing_words = [" do ", " does ", " is ", " are ", " should ", " in "]
                for word in possible_trailing_words:
                    if word in ingredient_name:
                        ingredient_name = ingredient_name.split(word)[0]
                        break
                ingredient_name = ingredient_name.strip()
            if not ingredient_name:
                msg += "Sorry, I can't understand your ingredient question. Please specify an ingredient name.\n"
                return msg
            ingredient = None
            for ingdt_candidate in self.recipe.ingredients:
                if ingdt_candidate.is_same_ingredient(ingredient_name):
                    ingredient = ingdt_candidate
                    break
            if not ingredient:
                msg += f"Sorry, I can't find the ingredient '{ingredient_name}'.\n"
            else:
                ingredient_str = action.get_ingredients_info_str(ingredient.name)
                if ingredient_str:
                    msg += f"You need {ingredient_str} in this step."
                else:
                    msg += f"There is probably no specific information available about '{ingredient_name}' in this particular step. "
                    msg += f"However, I find related information in the ingredients list: {ingredient}."
        else:
            msg += "Sorry, I can't understand your parameter-related question. Available parameters: time, temperature, ingredient (specify ingredient name).\n"
        return msg
    
    def ask_vague_what(self) -> str:
        # check if recipe is loaded
        self.check_recipe()
        
        action = self.recipe.get_action(self.current_action)
        msg = handle_fuzzy_what_questions_string(action.ingredients, action.tools)
        return msg
    
    def ask_vague_how(self) -> str:
        # check if recipe is loaded
        self.check_recipe()
        
        action = self.recipe.get_action(self.current_action)
        msg = handle_fuzzy_how_questions_string(action.sentence)
        return msg
    
    def ask_specific(self, question: str) -> str:
        # check if recipe is loaded
        self.check_recipe()
        
        msg = handle_specific_question_string(question)
        return msg
                
    def quit_recipe(self) -> str:
        if self.recipe is None:
            return "No recipe loaded. Nothing to quit."
        self.reset()
        return "Quitting recipe..."
    

if __name__ == "__main__":
    state_machine = RecipeRasaStateMachine()