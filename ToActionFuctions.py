import spacy
nlp = spacy.load('en_core_web_sm')
spacy_model = spacy.load("en_core_web_lg")




def findTool(ListSentence):
    toolList = []
    for i in range(len(ListSentence)):
        single = findToolSingle(ListSentence[i])
        if single == [] and i > 0:
            single = findToolSingle(ListSentence[i-1])
        toolList.append(single)
    return toolList

def findMethod(ListSentence):
    methodList = []
    for i in ListSentence:
        single1 = findAllVerbsSingle(i)
        single2 = findMethodSingle(i)
        single1.extend(single2)
        methodList.append(list(set(single1)))
    return methodList


#===================================================
# here is the supporting functions for above
#===================================================
#find tool
def findToolSingle(sentence):
    toolList = []
    sentence = sentence.lower()
    for i in tool_method_list["cooking_tools"]:
        if i.lower() in sentence:
            toolList.append(i)
    return toolList


#find primary cooking method
def findMethodSingle(sentence):
    methodllist = []
    sentence = sentence.lower()
    for i in tool_method_list["cooking_methods"]:
        if i.lower() in sentence:
            methodllist.append(i)
    return methodllist


#way 1 to find verb
def findAllVerbsSingle(sentence):
    doc = nlp(sentence)
    verbs = []
    for token in doc:
        if token.pos_ == "VERB" and not token.text.endswith("ed"):
            verbs.append(token.text)
    return list(set(verbs))


# way 2 to find verb
def findRelationVerbSingle(sentence):
    verblist = []
    spacy_output = spacy_model(sentence)
    for n in spacy_output.noun_chunks:
        if n.text == "You":
            continue
        verb = find_most_related_verb(n)
        if verb is not None:
            verblist.append(verb)
    return list(set(verblist))
def find_most_related_verb(noun_chunk: spacy.tokens.Span) -> [spacy.tokens.Token, None]:
    cur_token = noun_chunk.root

    while cur_token.head.pos_ != "VERB":
        if cur_token.head == cur_token:
            return None
        cur_token = cur_token.head
    return cur_token.head



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
    "refrigerator"
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
    "cook"
  ]
}