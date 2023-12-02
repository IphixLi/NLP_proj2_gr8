from fuzzywuzzy import fuzz
from transformationDB import transformations

def transform_ingredient_list(ingredient_list, transformation_type):
    transformation_dict=transformations[transformation_type]
    new_ingredients=[]
    for step in ingredient_list:
        new_step=[]
        for ingredient in step:
            # find matching ingredient in transformations
            matching_ingredient = find_closest_match(ingredient, transformation_dict)
            if matching_ingredient:
                new_step.append([ingredient, matching_ingredient])
            else:
                new_step.append([ingredient, ingredient])
        new_ingredients.append(new_step)
    return new_ingredients

# transformation for sentence list
def transfor_sentence_list(modified_ingredient_list, sentence_list):
    new_sentence_list=[]
    for idx, sentence in enumerate(sentence_list):
        pass
        

def find_closest_match(input_key, substitution_list):
    closest_match, match_val= max(substitution_list.items(), key=lambda x: fuzz.ratio(x[0], input_key))
    
    # You can adjust the threshold based on your preferences\
    similarity=fuzz.ratio(closest_match, input_key)
    # print("test??", input_key, ",", closest_match,",", match_val, similarity )
    if similarity > 70:
        return match_val
    else:
        return None
