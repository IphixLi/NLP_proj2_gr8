# NLP_proj2_gr8
project 2: Recipe parsing

# Github address

```
https://github.com/IphixLi/NLP_proj2_gr8.git
```

# Video link

```
https://drive.google.com/file/d/1dWgdnnDPVaz7t-pqxwcewQO484Yooud4/view?usp=sharing
```

# Package install

Please run the following command to get libraries and model files

```
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md
python -m spacy download en_core_web_lg
```

# To run the code

## Command Line Interface Version

```
pwd # NLP_proj2_gr8/
python main.py
```

## Rasa Chat-bot Version

```
cd rasa-try
pwd 				   # NLP_proj2_gr8/rasa-try
rasa train
rasa run actions &   	# need to kill with 'kill', or open another window
rasa shell
```

# Features

- Classes for parsing

    - Recipe (```recipe.py```)
        - hold two main data structures to save parsed data: step list and ingredient list
        - collect all methods, tools in this recipe used for overview
    - Ingredient (parsed based on tags) (```ingredient.py```)
        - quantity: turn it into float using several methods because variation of formats on websites
            - ½ -> 0.5
            - 1/2 -> 0.5
        - unit
        - name
        - preparation
    - Step: split into sub-steps called 'Action' (```action.py```)
        - The step on the website is too long, so we divided it based on '.' and ';'
        - Create a list of actions
        - Parsed information for actions together using ```to_*()``` functions
    - Action: sub-step (```action.py```)
        - temperature
        - ingredients
        - time
        - primary cooking methods
        - **[Optional]** other cooking methods used (``````)
            - turn imperative sentence to normal sentence
            - apply syntax analysis with spacy
        - tools
        - **[Optional]** ingredients_info (```Action.find_all_ingredients_info()```)
            - used for question answering and quantity scaling
            - extra quantity requirement in steps
            - example: "Step 2: Combine **3 cups water**..."

- Question answering (```handle_questions.py and main.py```)

    - step parameter (```RecipeStateMachine.handle_query() in main.py```)
        - time: used parsed data from Action
        - temperature: used parsed data from Action
        - ingredients: first check requirements in step, then check global list
    - specific: return links of google and youtube for this question (```handle_questions.py```)
    - vague what: return links for each tools / ingredients in this step (```handle_questions.py```)
    - vague how: parse possible actions from the current step and return links for each action (```handle_questions.py```)

- Transformation

    - vegan (```transformation.py and transformationDB.py```)
        - modify ingredient names, steps and recipe names
        - see external resources below
    - healthy (```transformation.py and transformationDB.py```)
        - modify ingredient names, steps and recipe names
        - see external resources below
    - Italian (```transformation.py and transformationDB.py```)
        - modify ingredient names, steps and recipe names
        - see external resources below
    - vegetarian (```transformation.py and transformationDB.py```)
        - modify ingredient names, steps and recipe names
        - see external resources below
    - quantity scaling (```quantity_transformation.py```)
        - change ingredient list by quantities
        - in each sentences, only change numbers if: 1. it’s related to ingredients; 2. no “each” in that sentence 
        - example: won't change 2 here because it's an average number: “2 slices of ham on each tortillas"

- User interaction

    - Command line interface

        - Input is concise

        - Use a state machine class to manage the recipe and control the state transition according to user input

        - Each state fulfills a type of user requests, including step navigation, transformation, question answering and abstract printing

            - get the overview, ingredients list, steps list to see if they want to use that recipe

            - transform **cumulatively** in transform mode
              - vegan
              - healthy
              - quantity scaling
              - Italian
              - vegetarian
              - revert to original
            - navigate between steps
              - next
              - prev
              - repeat
              - jump to another
              - back to first
            - ask questions in query mode
              - Specific questions (what is a tool/How to) (return youtube and google link)
              - Ask parameters in step
              - Vague how/what: guess users' questions in this step
            - other navigation
              - restart a new recipe
              - resume the current step or back to overview after transformation

    - **[Optional]** rasa chat-bot (```rasa-try/*```)
    
        - Both state transitions and user inputs are less restricted
        - Possible input examples for each kinds of intents in ```rasa-try/data/nlu.yml```
        - Assign custom actions to intent in ```rasa-try/data/rules.yml```
        - All knowledge in ```rasa-try/domain.yml```
        - Define custom actions to handle each intents where calling a singleton class to access the recipe data ```rasa-try/actions/*```
            - actions definitions: ```rasa-try/actions/actions.py```
            - singleton state machine class: ```rasa-try/actions/recipe_state.py```
            - other files copied from main directory with some modifications
        - Support intent
            - input_url
              - print_abstract
              - print_ingredients
              - print_all_actions
              - next_step
              - previous_step
              - repeat_step
              - restart_instructions
              - jump_to_step
              - ask_step_parameter
              - ask_vague_what
              - ask_vague_how
              - ask_specific
              - help
              - quit_recipe
        - Notice:
            - Transformation are not available
            - Output may vary with CLI due to out-dated code copy (output of CLI is the final version)

# External resouces

For the database of recipe alternatives, data was sources from from this former project.

https://raw.githubusercontent.com/amitadate/EECS-337-NLP-Project-02/master/Final_Submission/transformation_list.py
