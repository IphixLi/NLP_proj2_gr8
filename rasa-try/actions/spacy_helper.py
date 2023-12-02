import spacy
from typing import Union, List
from spacy import Language

def find_most_related_verb(noun_chunk: spacy.tokens.Span) -> Union[spacy.tokens.Token, None]:
    """Find the most related verb of a noun chunk (the closest ancestor that is a verb)."""
    cur_token = noun_chunk.root
    
    while cur_token.head.pos_ != "VERB":
        if cur_token.head == cur_token:
            return None
        cur_token = cur_token.head
    return cur_token.head

# find the possible ingredient index in spacy doc from the sentence (return -1 if not found)
def find_ingredient_index(doc: Language, ingredient: str) -> int:
    ingredient_words = ingredient.lower().split()
    
    for token in doc:
        if token.pos_ == "NOUN" and token.text in ingredient_words:
            return token.i
    return -1

def find_num_index_list(doc: Language) -> List[int]:
    idx_list = []
    for token in doc:
        if token.pos_ == "NUM" and token.dep_ == "nummod":
            idx_list.append(token.i)
    return idx_list