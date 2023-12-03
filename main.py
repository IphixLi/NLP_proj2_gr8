from enum import Enum
from typing import Callable

from recipe import Recipe
from handle_questions import is_vague_question, is_specific_question, handle_specific_question, handle_fuzzy_what_questions, handle_fuzzy_how_questions

class State(Enum):
    QUIT = -1
    RESTART = 0
    INPUT_URL = 1
    ABSTRACT = 2
    ACTION = 3
    FINISH = 4
    
class RecipeStateMachine:
    def __init__(self) -> None:
        self.state = State.INPUT_URL
        # two recipe objects, first used for revert back to original recipe, second used for current recipe
        # both initialized in input_url
        self.original_recipe = None
        self.recipe = None
        
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
            State.ABSTRACT: self.abstract,
            State.ACTION: self.action,
            State.FINISH: self.finish,
            State.RESTART: self.restart,
        }
        state_action = state_actions.get(self.state, lambda: None)
        if state_action:
            state_action()
    
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
                self.original_recipe = Recipe(url)
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
                'r': lambda: self.confirm_input(self.jump_to_restart),
                'q': lambda: self.confirm_input(self.jump_to_quit),
                'h': lambda: self.help_abstract()
            }

            if user_input in input_actions:
                confirm = input_actions[user_input]()
                if confirm:
                    return  
            else:
                print("Invalid input. Please enter 'i' for ingredients, 'd' for directions, 'r' to restart, or 'q' to quit.")
    
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
        Gives the user options for what to do next after printing the ingredients.
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
        self.recipe = None
        self.current_action = 0
    

if __name__ == "__main__":
    state_machine = RecipeStateMachine()
    state_machine.run()