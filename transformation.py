from fuzzywuzzy import fuzz
from transformationDB import transformations

def transform_ingredient_list(ingredient_list, transformation_type):
    transformation_dict=transformations[transformation_type]
    new_ingredients=[]
    for step in ingredient_list:
        new_step=[]
        for ingredient in step:
            # find matching ingredient in transformations
            matching_ingredient = transform_ingredient(ingredient,transformation_dict)
            if matching_ingredient!=ingredient:
                new_step.append([ingredient, matching_ingredient])
            else:
                new_step.append([ingredient, ingredient])
        new_ingredients.append(new_step)
    return new_ingredients

def transform_ingredient(ingredient, transformation_dict):
    matching_ingredient = find_closest_match(ingredient, transformation_dict)
    if matching_ingredient:
        return matching_ingredient
    else:
        return ingredient

# transformation for sentence list
def transform_sentence_list(modified_ingredient_list, ingredient_mappings, sentence_list, transformation_type):
    transformation_dict=transformations[transformation_type]
    new_sentence_list=[]
    for idx, sentence in enumerate(sentence_list):
        for i, ingr in enumerate(ingredient_mappings[idx]):
            from_official_name=transform_ingredient(ingr[1], transformation_dict )
            if from_official_name!=ingr[1]:
                sentence=sentence.replace(ingr[0],from_official_name)
            else:
                from_raw_name=transform_ingredient(ingr[0], transformation_dict)
                sentence=sentence.replace(ingr[0], from_raw_name)
        new_sentence_list.append(sentence)
    
    print("new: ", new_sentence_list, sentence_list)
    return new_sentence_list
        

def find_closest_match(input_key, substitution_list):
    closest_match, match_val= max(substitution_list.items(), key=lambda x: fuzz.ratio(x[0], input_key))
    
    # You can adjust the threshold based on your preferences\
    similarity=fuzz.ratio(closest_match, input_key)
    # print("test??", input_key, ",", closest_match,",", match_val, similarity )
    if similarity > 70:
        return match_val
    else:
        return None


# given list of sentences replace words in sentences with the ones near them for example 
# [[['flour tortillas', 'lettuce leaves'], ['deli ham', 'deli ham']], [['flour tortillas', 'lettuce leaves'], ['olby-Jack cheese', 'olby-Jack cheese']], [['flour tortillas', 'lettuce leaves']], []]
# ingredient_list:  [[]]

# so where there is 