from enum import Enum
from typing import Callable
from copy import deepcopy
from fractions import Fraction
import logging
logging.getLogger().setLevel(logging.ERROR)

from recipe import Recipe
from quantity_transformation import transform_quantity
from transformation import transform_recipe_type
from handle_questions import is_vague_question, is_specific_question, handle_specific_question, handle_fuzzy_what_questions, handle_fuzzy_how_questions

class State(Enum):
    QUIT = -1
    RESTART = 0
    INPUT_URL = 1
    TRANSFORM = 2
    ABSTRACT = 3
    ACTION = 4
    FINISH = 5
    
class RecipeStateMachine:
    def __init__(self) -> None:
        self.state = State.INPUT_URL
        # two recipe objects, first used for revert back to original recipe, second used for current recipe
        # both initialized in input_url
        self.original_recipe = None
        self.recipe = None
        self.current_transformations = self.get_original_transformations()
        self.current_action = 0
        
        print("Welcome to the Recipe Parser!")
        print("Follow the prompts to navigate through the recipe steps.")
        print("You can start by entering the URL of a recipe.\n")
        
    def run(self) -> None:
        """
        Runs the state machine. In each iteration, run the current state and ask for user input to update the state.
        """
        while self.state != State.QUIT:
            self.run_state()
    
    def run_state(self) -> None:
        """Runs the current state and the transition to the next state."""
        state_actions = {
            State.INPUT_URL: self.input_url,
            State.TRANSFORM: self.handle_transform,
            State.ABSTRACT: self.abstract,
            State.ACTION: self.action,
            State.FINISH: self.finish,
            State.RESTART: self.restart,
        }
        state_action = state_actions.get(self.state, lambda: None)
        if state_action:
            state_action()
        else:
            raise ValueError(f"Invalid state: {self.state}")
    
    def input_url(self) -> None:
        """
        Prompts the user for a recipe URL until a valid Recipe object is created or the user decides to quit.
        """
        print("\nPlease enter the URL of the recipe you wish to use,")
        print("or type 'q' to quit and return to the main menu.")
        
        while True:
            print()
            url = input("Recipe URL (type 'q' to quit): ").strip()
            if url.lower() == "q":
                self.state = State.QUIT
                return
            try:
                print()
                print(f"Fetching recipe from {url}...")
                self.recipe = Recipe(url)
                self.original_recipe = deepcopy(self.recipe)
                self.state = State.ABSTRACT
                return
            except Exception as e:
                print(f"Error while fetching the recipe: {e}. Please try again.")
                
    def confirm_input(self, yes_handler: Callable[[], bool]) -> bool:
        """
        Asks the user to confirm the input. If user enters 'y', calls yes_handler and returns True. Otherwise, returns False.
        """
        if yes_handler == self.jump_to_restart:
            input_prompt = "Are you sure you want to restart with a new recipe? (y/n): "
        elif yes_handler == self.jump_to_quit:
            input_prompt = "Are you sure you want to quit? (y/n): "
        else:
            input_prompt = "Are you sure? (y/n): "
        
        user_input = input(input_prompt).strip().lower()
        if user_input == "y":
            return yes_handler()
        else:
            return False
    
    def jump_to_first_action(self) -> bool:
        """
        Jumps to the first action of the recipe. Returns True to confirm the jump.
        """
        self.state = State.ACTION
        self.current_action = 0
        return True
    
    def jump_to_prev_action(self) -> bool:
        """
        Jumps to the previous action of the recipe. Returns True to confirm the jump.
        """
        if self.current_action - 1 < 0:
            print("You are at the first step. Doing so will go back to the recipe overview.")
            return self.confirm_input(self.jump_to_abstract)
        self.current_action -= 1
        return True

    def jump_to_next_action(self) -> bool:
        """
        Jumps to the next action of the recipe. Returns True to confirm the jump.
        """
        if self.current_action + 1 >= self.recipe.num_actions:
            print("You are at the last step. Doing so will end the recipe.")
            return self.confirm_input(self.jump_to_finish)
        self.current_action += 1
        return True
    
    def jump_to_specific_action(self, user_input: str) -> bool:
        """
        Jump to a specific action of the recipe. Returns True to confirm the jump; False if the input is invalid or out of bounds.
        
        Input is of the form 'j [number]', where number is the step number to jump to.
        """
        try:
            jump_to = int(user_input.split()[1])
            if jump_to < 1 or jump_to > self.recipe.num_actions:
                print(f"Invalid step number. Please enter a number between 1 and {self.recipe.num_actions}.")
                return False
            self.current_action = jump_to - 1
            self.state = State.ACTION
            return True
        except:
            print(f"Invalid input. Please enter 'j [number]' to jump to a specific step.")
            return False
    
    def jump_to_restart(self) -> bool:
        """
        Jump to the restart state. Returns True to confirm the jump.
        """
        self.state = State.RESTART
        return True
    
    def jump_to_quit(self) -> bool:
        """
        Jump to the quit state. Returns True to confirm the jump.
        """
        self.state = State.QUIT
        return True
    
    def jump_to_finish(self) -> bool:
        """
        Jump to the finish state. Returns True to confirm the jump.
        """
        self.state = State.FINISH
        return True
    
    def jump_to_abstract(self) -> bool:
        """
        Jump to the abstract state. Returns True to confirm the jump.
        """
        self.state = State.ABSTRACT
        return True
    
    def jump_to_transform(self) -> bool:
        """
        Jump to the transform state. Returns True to confirm the jump.
        """
        self.state = State.TRANSFORM
        return True

    def help_transform(self) -> None:
        print()
        print("You are in the transform mode. What would you like to do next? All transformations are CUMULATIVE.")
        print(" - Enter 'quant [scale factor]' to scale the recipe by a factor.")
        print(" - Enter 'vegan' to make the recipe vegan.")
        print(" - Enter 'healthy' to make the recipe healthy.")
        print(" - Enter 'r' to revert back to the original recipe.")
        print(" - Enter 'h' to see this help message again.")
        print(" - Enter 'q' to quit transform mode. You can choose to save all the transformations to the recipe or not.")
    
    def confirm_transform(self) -> bool:
        """
        Asks the user to confirm the transformation. If user enters 'y', calls yes_handler and returns True. Otherwise, returns False.
        """
        print()
        user_input = input("Are you sure you want to save the transformation to the recipe? (y/n): ").strip().lower()
        if user_input == "y":
            return True
        else:
            return False
    
    def back_to_abstract_or_repeat(self) -> None:
        print()
        print("Do you want to go back to the recipe overview or repeat the current step?")
        print(" - Enter 'o' to go back to the recipe overview.")
        print(" - Enter 'r' to resume the current step.")
        user_input = input('Your choice (enter "o" or "r"): ').strip().lower()
        if user_input == 'o':
            self.jump_to_abstract()
        else:
            pass
    
    def get_original_transformations(self) -> dict:
        return {
            'quantity': 1.0,
            'vegan': False,
            'healthy': False,
        }
        
    def handle_transform(self, ask_repeat=False) -> bool:
        self.help_transform()
        new_transformations = deepcopy(self.current_transformations)
        use_revert = False
        
        while True:
            print()
            user_input = input("[Transform mode] Your choice (enter 'h' for help): ").strip().lower()
            if user_input == 'q':
                break
            elif user_input == 'h':
                self.help_transform()
            elif user_input.startswith('quant'):
                try:
                    scale_factor = float(Fraction(user_input.split()[1]))
                    if scale_factor <= 0:
                        print("Invalid scale factor. Scale factor must be greater than 0.")
                    else:
                        new_transformations['quantity'] *= scale_factor
                        print(f"The recipe will be scaled by a factor of {new_transformations['quantity']} after quitting transform mode (compared with the original recipe).")
                except:
                    print("Invalid input. Please enter 'quant [scale factor]' to scale the recipe by a factor. Scale factor must be a number greater than 0.")
            elif user_input == 'vegan':
                if new_transformations['vegan']:
                    if self.current_transformations['vegan'] and not use_revert:
                        print("The recipe is already vegan.")
                    else:
                        print("The new recipe (after transformation) is already vegan.")
                else:
                    new_transformations['vegan'] = True
                    print("The recipe will be transformed to vegan after quitting transform mode.")
            elif user_input == 'healthy':
                if new_transformations['healthy']:
                    if self.current_transformations['healthy'] and not use_revert:
                        print("The recipe is already healthy.")
                    else:
                        print("The new recipe (after transformation) is already healthy.")
                else:
                    new_transformations['healthy'] = True
                    print("The recipe will be transformed to healthy after quitting transform mode.")
            elif user_input == 'r':
                new_transformations = self.get_original_transformations()
                use_revert = True
                print("The recipe will be reverted back to the original recipe and later transformations will be based on the original recipe.")
            else:
                print(f"'{user_input}' is not a valid command. Enter 'h' for help.")
        
        if self.confirm_transform():
            self.transform_recipe(new_transformations)
            print("Transformations completed.")
        if ask_repeat:
            self.back_to_abstract_or_repeat()
        else:
            print("Will be back to the recipe overview.")
            self.jump_to_abstract()
        print("Quitting transform mode...")
        print()
        return True
    
    def get_modification_str(self, new_transformations: dict) -> str:
        """
        Returns a string that describes the modifications made to the recipe.
        """
        modification_list = []
        if new_transformations['quantity'] != 1.0:
            modification_list.append(f"{new_transformations['quantity']}x")
        if new_transformations['vegan']:
            modification_list.append("vegan")
        if new_transformations['healthy']:
            modification_list.append("healthy")
        if modification_list:
            return f"{'+'.join(modification_list)}"
        return ""
        
    
    def transform_recipe(self, new_transformations: dict) -> None:
        """
        Transforms the recipe based on the given transformations.
        """
        # TODO: implement vegan and healthy transformations
        # check if we need to revert back to the original recipe
        print(f"Current recipe: {self.current_transformations}")
        print(f"New recipe:     {new_transformations}")
        cur_vegan = self.current_transformations['vegan']
        cur_healthy = self.current_transformations['healthy']
        new_vegan = new_transformations['vegan']
        new_healthy = new_transformations['healthy']
        if (cur_vegan and not new_vegan) or (cur_healthy and not new_healthy):
            print("Reverting back to the original recipe...")
            self.recipe = deepcopy(self.original_recipe)
            self.current_transformations = self.get_original_transformations()
        # transform the recipe by combining the current transformations and the new transformations
        if new_vegan:
            print("Transforming to vegan...")
            new_sentences_list_type, new_ingredients_type = transform_recipe_type(self.recipe, 'vegan')
            self.recipe.transform(new_sentences_list_type, new_ingredients_type, modification=self.get_modification_str(new_transformations))
        if new_healthy:
            print("Transforming to healthy...")
            new_sentences_list_type, new_ingredients_type = transform_recipe_type(self.recipe, 'healthy')
            self.recipe.transform(new_sentences_list_type, new_ingredients_type, modification=self.get_modification_str(new_transformations))
        if new_transformations['quantity'] != self.current_transformations['quantity']:
            print(f"Scaling quantity by {new_transformations['quantity']}...")
            new_sentences_list, new_ingredients = transform_quantity(self.recipe, new_transformations['quantity'] / self.current_transformations['quantity'])
            self.recipe.transform(new_sentences_list, new_ingredients, modification=self.get_modification_str(new_transformations))
        self.current_transformations = new_transformations
        
    def abstract(self) -> None:
        self.print_abstract()
        self.input_abstract()

    def print_abstract(self) -> None:
        """
        Prints the abstract of the recipe.
        """
        print("\nRecipe Overview:")
        print("-------------------")
        self.recipe.print_abstract()
    
    def help_abstract(self) -> None:
        """
        Gives the user options for what to do next after printing the abstract.
        """
        print()
        print("You are at the overview stage of the recipe. What would you like to do next?")
        print(" - Enter 'i' to list the ingredients in detail.")
        print(" - Enter 's' to list all the steps.")
        print(" - Enter 'd' to start the directions.")
        print(" - Enter 't' to transform the recipe.")
        print(" - Enter 'r' to restart with a new recipe.")
        print(" - Enter 'q' to quit.")
        print(" - Enter 'h' to see this help message again.")
    
    def input_abstract(self) -> None:
        """
        Prompts the user for input after printing the abstract.
        """
        self.help_abstract()
        while True:
            print()
            user_input = input("Your choice (enter 'h' for help): ").strip().lower()

            input_actions = {
                'i': lambda: self.print_ingredients(),
                's': lambda: self.list_actions(),
                'd': lambda: self.jump_to_first_action(),
                't': lambda: self.jump_to_transform(),
                'r': lambda: self.confirm_input(self.jump_to_restart),
                'q': lambda: self.confirm_input(self.jump_to_quit),
                'h': lambda: self.help_abstract()
            }

            if user_input in input_actions:
                confirm = input_actions[user_input]()
                if confirm:
                    return  
            else:
                print("Invalid input. Enter 'h' for help.")
    
    def list_actions(self) -> None:
        """
        Lists all the actions in the recipe.
        """
        print("\nRecipe Steps:")
        print("-------------------")
        self.recipe.list_actions()
    
    def print_ingredients(self) -> None:
        """Prints the ingredients of the recipe."""
        print("\nRecipe Ingredients:")
        print("-------------------")
        self.recipe.print_ingredients()
    
    def action(self) -> None:
        self.print_action()
        self.input_action()
    
    def print_action(self) -> None:
        """Prints the action of the recipe with the given action index."""
        print(f"\nStep {self.current_action + 1} / {self.recipe.num_actions} of the recipe:")
        print("-------------------")
        self.recipe.print_action(self.current_action)
    
    def help_action(self) -> None:
        """
        Gives the user options for what to do next after printing the ingredients.
        """
        print()
        print(f"You are at step {self.current_action + 1} / {self.recipe.num_actions} of the recipe. What would you like to do next?")
        print(" - Enter 'n' to proceed to the next step.")
        print(" - Enter 'p' to go back to the previous step.")
        print(" - Enter 'rpt' to repeat the current step.")
        print(" - Enter 'query' to ask a question about the current step.")
        print(" - Enter 't' to transform the recipe.")
        print(" - Enter 'i' to list the ingredients in detail.")
        print(" - Enter 'o' to list the overview of the recipe.")
        print(" - Enter 'd' to restart the directions.")
        print(" - Enter 'j [number]' to jump to a specific step.")
        print(" - Enter 'h' to see this help message again.")
        print(" - Enter 'r' to restart with a new recipe.")
        print(" - Enter 'q' to quit.")
    
    def input_action(self) -> None:
        """
        Prompts the user for input after printing the ingredients.
        """
        self.help_action()
        while True:
            print()
            user_input = input("Your choice (enter 'h' for help): ").strip().lower()
            
            input_actions = {
                'n': lambda: self.jump_to_next_action(),
                'p': lambda: self.jump_to_prev_action(),
                't': lambda: self.handle_transform(ask_repeat=True),
                'i': lambda: self.print_ingredients(),
                'o': lambda: self.print_abstract(),
                'd': lambda: self.jump_to_first_action(),
                'r': lambda: self.confirm_input(self.jump_to_restart),
                'q': lambda: self.confirm_input(self.jump_to_quit),
                'h': lambda: self.help_action(),
                'rpt': lambda: True, # Do nothing
                'query': lambda: self.handle_query(),
            }
            
            if user_input in input_actions:
                confirm = input_actions[user_input]()
                if confirm:
                    return
            elif user_input.startswith('j'):
                confirm = self.jump_to_specific_action(user_input)
                if confirm:
                    return
            else:
                print("Invalid input. Enter 'h' for help.")
    
    def help_query(self) -> None:
        """
        Gives the user options for what to do next in query mode.
        """
        print()
        print("You are in the query mode. What would you like to do next?")
        print(" - Enter '(what is|how to) [some specific content]' to ask a specific question.")
        print(" - Enter 'vague (what|how)' to see some questions you might ask about the step.")
        print(" - Enter 's' to print the current step.")
        print(" - Enter 'i [ingredient name]' to see the details of an ingredient.")
        print(" - Enter 'temp' to see the temperature information of the current step.")
        print(" - Enter 'time' to see the time information of the current step.")
        print(" - Enter 'h' to see this help message again.")
        print(" - Enter 'f' to see question formats.")
        print(" - Enter 'q' to quit query mode.")
    
    def print_question_formats(self) -> None:
        print()
        print("Question formats:")
        print("1. (what is|how to) [some specific content] (e.g. what is a whisk; how to preheat oven)")
        print("2. vague (what|how) (e.g. vague what; vague how)")
        print("3. i [ingredient name] (e.g. i flour)")
        print("4. temp")
        print("5. time")
    
    def handle_query(self) -> bool:
        self.help_query()
        
        while True:
            print()
            user_input = input("[Query mode] Your choice (enter 'h' for help): ").strip().lower()
            if user_input == 'q':
                print("Quitting query mode...")
                print()
                return True
            elif user_input == 's':
                self.print_action()
            elif user_input == 'h':
                self.help_query()
            elif user_input == 'f':
                self.print_question_formats()
            elif 'i ' in user_input:
                action = self.recipe.get_action(self.current_action)
                ingredient_name = user_input[2:]
                # find the valid ingredient name from the global ingredient list
                ingredient = None
                for ingdt_candidate in self.recipe.ingredients:
                    if ingdt_candidate.is_same_ingredient(ingredient_name):
                        ingredient = ingdt_candidate
                        break
                if not ingredient:
                    print(f"Sorry, I can't find the ingredient '{ingredient_name}'.")
                    continue
                # use the valid ingredient name to find ingredient info in the current step
                # if failed, print the ingredient info in the ingredients list
                ingredient_str = action.get_ingredients_info_str(ingredient.name)
                if ingredient_str:
                    print(f"You need {ingredient_str} in this step.")
                else:
                    print(f"There is probably no specific information available about '{ingredient_name}' in this particular step. " + \
                          f"However, I find related information in the ingredients list: {ingredient}.")
            elif user_input == 'temp':
                action = self.recipe.get_action(self.current_action)
                temperature_str = action.get_temperature_str()
                if temperature_str:
                    print(f"The temperature for this step is {temperature_str}.")
                else:
                    print("Sorry, I can't find temperature information for this step.")
            elif user_input == 'time':
                action = self.recipe.get_action(self.current_action)
                time_str = action.get_time_str()
                if time_str:
                    print(f"The time for this step is {time_str}.")
                else:
                    print("Sorry, I can't find time information for this step.")
            elif is_specific_question(user_input):
                handle_specific_question(user_input)
            elif is_vague_question(user_input):
                cur_action = self.recipe.get_action(self.current_action)
                if "how" in user_input:
                    handle_fuzzy_how_questions(cur_action.sentence)
                else:
                    handle_fuzzy_what_questions(cur_action.ingredients, cur_action.tools)
            else:
                print(f"'{user_input}' is neither a question nor a valid command. Enter 'h' for help, or 'f' for question formats.")
                
    
    def finish(self) -> None:
        self.print_finish()
        self.input_finish()
    
    def print_finish(self) -> None:
        """
        Prints the final message.
        """
        print("\nYou've reached the end of the recipe. Enjoy your meal!")
    
    def help_finish(self) -> None:
        """
        Gives the user options for what to do next after printing the ingredients.
        """
        print()
        print("You just finish the recipe. What would you like to do next?")
        print(" - Enter 'r' to start with a new recipe.")
        print(" - Enter 'i' to list the ingredients in detail.")
        print(" - Enter 't' to transform the recipe.")
        print(" - Enter 'o' to list the overview of the recipe.")
        print(" - Enter 'd' to restart the directions.")
        print(" - Enter 'j [number]' to jump to a specific step.")
        print(" - Enter 'h' to see this help message again.")
        print(" - Enter 'q' to quit.")
        
    def input_finish(self) -> None:
        self.help_finish()
        while True:
            print()
            user_input = input("Your choice (enter 'h' for help): ").strip().lower()
            
            input_actions = {
                'i': lambda: self.print_ingredients(),
                't': lambda: self.jump_to_transform(),
                'o': lambda: self.print_abstract(),
                'd': lambda: self.jump_to_first_action(),
                'r': lambda: self.confirm_input(self.jump_to_restart),
                'q': lambda: self.confirm_input(self.jump_to_quit),
                'h': lambda: self.help_finish(),
            }
            
            if user_input in input_actions:
                confirm = input_actions[user_input]()
                if confirm:
                    return
            elif user_input.startswith('j'):
                confirm = self.jump_to_specific_action(user_input)
                if confirm:
                    return
            else:
                print("Invalid input. Enter 'h' for help.")
        
    
    def restart(self) -> None:
        """Restarts the state machine."""
        self.state = State.INPUT_URL
        self.original_recipe = None
        self.recipe = None
        self.current_transformations = {'quantity': 1,'vegan': False, 'healthy': False}
        self.current_action = 0
    

if __name__ == "__main__":
    state_machine = RecipeStateMachine()
    state_machine.run()