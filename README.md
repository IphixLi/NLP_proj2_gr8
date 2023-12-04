# NLP_proj2_gr8
project 2: Recipe parsing

# Github address

```
https://github.com/IphixLi/NLP_proj2_gr8.git
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
rasa run actions &   	# need to kill with 'kill', or open another window
rasa shell
```

# Features

- Classes for parsing
    - Recipe
    - Ingredient
    - Step: split into sub-steps called 'Action'
    - Action
        - temperature
        - ingredients
        - time
        - primary methods
        - other methods
        - tools
- Question answering
    - step parameter
        - time
        - temperature
        - ingredients
    - specific
    - vague what
    - vague how
- Transformation
    - vegan
    - healthy
    - quantity scaling
- User interaction
    - command line interface
    - rasa chat-bot


# external resouces

For the database of recipe alternatives, data was sources from from this former project.

https://raw.githubusercontent.com/amitadate/EECS-337-NLP-Project-02/master/Final_Submission/transformation_list.py