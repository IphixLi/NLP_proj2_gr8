import spacy

from typing import Union

def find_most_related_verb(noun_chunk: spacy.tokens.Span) -> Union[spacy.tokens.Token, None]:
    """Find the most related verb of a noun chunk (the closest ancestor that is a verb)."""
    cur_token = noun_chunk.root
    
    while cur_token.head.pos_ != "VERB":
        if cur_token.head == cur_token:
            return None
        cur_token = cur_token.head
    return cur_token.head