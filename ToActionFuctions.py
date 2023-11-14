import spacy
import re
nlp = spacy.load('en_core_web_sm')
spacy_model = spacy.load("en_core_web_lg")

def findTool(ListSentence):
    toolList = []
    for i in range(len(ListSentence)):
        single = findToolSingle(imperative_to_normal(ListSentence[i]))
        if single == [] and i > 0:
            single = toolList[-1]
        toolList.append(single)
    return toolList

def findMethod(ListSentence):
    methodList = []
    for i in ListSentence:
        single1 = findAllVerbSingle(imperative_to_normal(i))
        single2 = findMethodSingle(imperative_to_normal(i))
        single1.extend(single2)
        single =list(set(single1)) 
        for j in single:
            if j in tool_method_list["bad_verb"]:
                single.remove(j)
        methodList.append(single)
    return methodList


def answerVague(sentence):
    RelationList = findRelationVerbSingle(imperative_to_normal(sen))
    temp = []
    temp2 = []
    returnList = []
    for i in RelationList:
        if str(i[0]) not in temp:
            if temp != []:
                temp2.append(temp)
                temp = []
            temp.append(str(i[0]))
            temp.append(str(i[1]))
        else:
            temp.append(str(i[1]))

    temp2.append(temp)

    for item in temp2:
        index1 = sen.index(item[0])
        index2 = sen.index(item[-1])
        returnList.append(sen[index1:index2+len(item[-1])])
        
    return returnList


#===================================================
# here is the supporting functions for above
#===================================================
#find tool
def findToolSingle(sentence):
    toolList = []
    sentence = sentence.lower()
    for i in tool_method_list["cooking_tools"]:
        if i in sentence:
            toolList.append(i)
    return toolList


#find primary cooking method
def findMethodSingle(sentence):
    methodllist = []
    sentence = sentence.lower()
    for i in tool_method_list["cooking_methods"]:
        if match_whole_word(sentence, i):
            methodllist.append(i)
    return methodllist


#find verb
def findAllVerbSingle(sentence):
    doc = nlp(sentence)
    verbs = []
    for token in doc:
        if token.pos_ == "VERB" and not token.text.endswith("ed"):
            verbs.append(token.lemma_)
    return list(set(verbs))


#find verb noun relation
def findRelationVerbSingle(sentence):
    verblist = []
    spacy_output = spacy_model(sentence)
    for n in spacy_output.noun_chunks:
        if n.text == "You":
            continue
        verb = find_most_related_verb(n)
        if verb is not None:
            verblist.append([verb,n])
    return verblist
def find_most_related_verb(noun_chunk: spacy.tokens.Span) -> [spacy.tokens.Token, None]:
    cur_token = noun_chunk.root

    while cur_token.head.pos_ != "VERB":
        if cur_token.head == cur_token:
            return None
        cur_token = cur_token.head
    return cur_token.head

#match
def match_whole_word(text, word):
    # The pattern will look for the word surrounded by word boundaries
    pattern = r'\b' + re.escape(word) + r'(|ing)\b'
    return re.search(pattern, text) is not None

#normalization
def imperative_to_normal(sentence: str) -> str:
    try:
        i = sentence.index(",")
        if " " not in sentence[:i]:
            sentence = sentence[i+2 :]
    except Exception:
        pass
    if sentence.endswith("."):
        return f"You {sentence[0].lower()}{sentence[1:]}"
    else:
        return f"You {sentence[0].lower()}{sentence[1:]}."



#keywordlist
tool_method_list = {
  "cooking_tools": [
    "pot",
    "pan",
    "knife",
    "cutting board",
    "mixing bowl",
    "measuring cup",
    "measuring spoon",
    "whisk",
    "spatula",
    "tong",
    "wooden spoon",
    "slotted spoon",
    "ladle",
    "skillet",
    "saucepan",
    "oven",
    "stockpot",
    "roasting pan",
    "baking sheet",
    "rolling pin",
    "pastry brush",
    "kitchen shears",
    "grater",
    "zester",
    "vegetable peeler",
    "can opener",
    "colander",
    "strainer",
    "mixing spoon",
    "silicone spatula",
    "meat thermometer",
    "oven mitts",
    "pot holder",
    "kitchen timer",
    "food processor",
    "blender",
    "stand mixer",
    "hand mixer",
    "mortar and pestle",
    "pastry cutter",
    "mandoline slicer",
    "garlic press",
    "seafood crackers",
    "refrigerator",
    "grill",
    "twine" 
  ],
    "bad_verb":[
        "have",
        "let",
        "use",
        "depend",
        "approximate",
        "continue"
    ],
      "cooking_methods": [
    "bake",
    "roast",
    "broil",
    "grill",
    "pan-fry",
    "deep-fry",
    "sauté",
    "stir-fry",
    "simmer",
    "boil",
    "steam",
    "poach",
    "blanch",
    "pressure cook",
    "braise",
    "smoke",
    "sear",
    "glaze",
    "sous-vide",
    "marinate",
    "chill",
    "freeze",
    "defrost",
    "ferment",
    "caramelize",
    "toast",
    "infuse",
    "reduce",
    "whip",
    "fold",
    "knead",
    "mix",
    "blend",
    "emulsify",
    "froth",
    "macerate",
    "stir",
    "heat",
    "cook",
    "pour"
  ]
}
