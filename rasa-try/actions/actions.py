import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from .recipe_state import RecipeRasaStateMachine

#  - action_process_recipe_url
class ActionProcessRecipeURL(Action):
    def name(self) -> str:
        return "action_process_recipe_url"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Retrieve the URL from the slot
        recipe_url = tracker.get_slot("recipe_url")

        if recipe_url:
            # Send a response back to the user
            try:
                dispatcher.utter_message(text=f"Processing recipe from {recipe_url}...")
                recipe = RecipeRasaStateMachine()
                recipe.set_url(recipe_url)
                msg = recipe.parse_recipe()
                dispatcher.utter_message(text=msg)
            except Exception as e:
                dispatcher.utter_message(text=f"{e}")
        else:
            # Ask for the URL if not provided
            dispatcher.utter_message(text="Please provide the recipe URL. The URL should include 'https://www.allrecipes.com/'")

        return [SlotSet("recipe_url", None)]

#   - action_print_abstract
class ActionPrintAbstract(Action):
    def name(self) -> str:
        return "action_print_abstract"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            dispatcher.utter_message(text="Fetching abstract...")
            recipe = RecipeRasaStateMachine()
            msg = recipe.get_abstract_msg()
            dispatcher.utter_message(text=msg)
        except Exception as e:
            dispatcher.utter_message(text=f"{e}")
        return []

#   - action_print_ingredients
class ActionPrintIngredients(Action):
    def name(self) -> str:
        return "action_print_ingredients"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
        try:
            dispatcher.utter_message(text="Fetching ingredients...")
            recipe = RecipeRasaStateMachine()
            msg = recipe.get_ingredients_msg()
            dispatcher.utter_message(text=msg)
        except Exception as e:
            dispatcher.utter_message(text=f"{e}")
        return []

#   - action_print_all_actions
class ActionPrintAllActions(Action):
    def name(self) -> str:
        return "action_print_all_actions"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
        try:
            dispatcher.utter_message("Fetching all steps...")
            recipe = RecipeRasaStateMachine()
            msg = recipe.get_all_actions_msg()
            dispatcher.utter_message(text=msg)
        except Exception as e:
            dispatcher.utter_message(text=f"{e}")
        return []

#   - action_next_step
class ActionNextStep(Action):
    def name(self) -> str:
        return "action_next_step"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
        try:
            dispatcher.utter_message(text="Moving to the next step...")
            recipe = RecipeRasaStateMachine()
            msg = recipe.next_step()
            dispatcher.utter_message(text=msg)
        except Exception as e:
            dispatcher.utter_message(text=f"{e}")
        return []
    
#   - action_previous_step
class ActionPreviousStep(Action):
    def name(self) -> str:
        return "action_previous_step"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
        try:
            dispatcher.utter_message(text="Back to the previous step...")
            recipe = RecipeRasaStateMachine()
            msg = recipe.prev_step()
            dispatcher.utter_message(text=msg)
        except Exception as e:
            dispatcher.utter_message(text=f"{e}")
        return []

#  - action_repeat_step
class ActionRepeatStep(Action):
    def name(self) -> str:
        return "action_repeat_step"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
        try:
            dispatcher.utter_message(text="Repeating the current step...")
            recipe = RecipeRasaStateMachine()
            msg = recipe.repeat_step()
            dispatcher.utter_message(text=msg)
        except Exception as e:
            dispatcher.utter_message(text=f"{e}")
        return []

#   - action_restart_instructions
class ActionRestartInstructions(Action):
    def name(self) -> str:
        return "action_restart_instructions"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
        try:
            dispatcher.utter_message(text="Restarting the directions...")
            recipe = RecipeRasaStateMachine()
            msg = recipe.restart_instructions()
            dispatcher.utter_message(text=msg)
        except Exception as e:
            dispatcher.utter_message(text=f"{e}")
        return []

#   - action_jump_to_step
class ActionJumpToStep(Action):
    def name(self) -> str:
        return "action_jump_to_step"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:    
        
        step_number = tracker.get_slot("step_index")
        if not step_number:
            dispatcher.utter_message(text="Please provide the step number.")
            return [SlotSet("step_index", None)]
        
        print(step_number)
        match = re.search(r'\d+', step_number)
        if not match:
            dispatcher.utter_message(text="Please provide the step number.")
            return [SlotSet("step_index", None)]
        
        step_number = match.group()
        try:
            dispatcher.utter_message(text=f"Jumping to step {step_number}...")
            recipe = RecipeRasaStateMachine()
            msg = recipe.jump_to_step(int(step_number))
            dispatcher.utter_message(text=msg)
        except Exception as e:
            dispatcher.utter_message(text=f"{e}")
        return [SlotSet("step_index", None)]

#   - action_ask_step_parameter
class ActionAskStepParameter(Action):
    def name(self) -> str:
        return "action_ask_step_parameter"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:    
        
        latest_message = tracker.latest_message['text']
        ingredient = tracker.get_slot("ingredient")
        recipe = RecipeRasaStateMachine()
        msg = recipe.ask_step_parameter(latest_message, ingredient)
        dispatcher.utter_message(text=msg)
        return []

#   - action_ask_vague_what
class ActionAskVagueWhat(Action):
    def name(self) -> str:
        return "action_ask_vague_what"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:    
        
        dispatcher.utter_message(text="Answering vague 'what' question...")
        recipe = RecipeRasaStateMachine()
        msg = recipe.ask_vague_what()
        dispatcher.utter_message(text=msg)
        return []

#   - action_ask_vague_how
class ActionAskVagueHow(Action):
    def name(self) -> str:
        return "action_ask_vague_how"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:    
        
        dispatcher.utter_message(text="Answering vague 'how to' question...")
        recipe = RecipeRasaStateMachine()
        msg = recipe.ask_vague_how()
        dispatcher.utter_message(text=msg)
        return []

#   - action_ask_specific
class ActionAskSpecific(Action):
    def name(self) -> str:
        return "action_ask_specific"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:    
        
        dispatcher.utter_message(text="Answering specific question...")
        latest_message = tracker.latest_message['text']
        recipe = RecipeRasaStateMachine()
        msg = recipe.ask_specific(latest_message)
        dispatcher.utter_message(text=msg)
        return []

#   - action_help
class ActionHelp(Action):
    def name(self) -> str:
        return "action_help"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
        msg = """
            You can ask me to print the abstract, print the ingredients, or print the steps. You can also ask me to print a specific step by saying 'print step 3'.
        """
        dispatcher.utter_message(text=msg)
        return []

#   - action_quit_recipe
class ActionQuitRecipe(Action):
    def name(self) -> str:
        return "action_quit_recipe"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
        recipe = RecipeRasaStateMachine()
        msg = recipe.quit_recipe()
        dispatcher.utter_message(text=msg)
        return []
    