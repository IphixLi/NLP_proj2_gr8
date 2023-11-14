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
        single = findAllVerbsSingle(i)
        methodList.append(single)
    return methodList

def findPrimeMethod(ListSentence):
    primeMethod = []
    for i in ListSentence:
        single = findMethodSingle(i)
        primeMethod.extend(single)
    return list(set(primeMethod))



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
    "Pot",
    "pan",
    "knife",
    "Cutting board",
    "Mixing bowl",
    "measuring cup",
    "measuring spoon",
    "Whisk",
    "Spatula",
    "Tong",
    "Wooden spoon",
    "Slotted spoon",
    "Ladle",
    "Skillet",
    "Saucepan",
    "oven",
    "Stockpot",
    "Roasting pan",
    "Baking sheet",
    "Rolling pin",
    "Pastry brush",
    "Kitchen shears",
    "Grater",
    "Zester",
    "Vegetable peeler",
    "Can opener",
    "Colander",
    "strainer",
    "Mixing spoon",
    "Silicone spatula",
    "Meat thermometer",
    "Oven mitts",
    "Pot holder",
    "Kitchen timer",
    "Food processor",
    "Blender",
    "Stand mixer",
    "Hand mixer",
    "Mortar and pestle",
    "Pastry cutter",
    "Mandoline slicer",
    "Garlic press",
    "Seafood crackers",
    "refrigerator"
  ],
      "cooking_methods": [
    "Bake",
    "Roast",
    "Broil",
    "Grill",
    "Pan-fry",
    "Deep-fry",
    "Sauté",
    "Stir-fry",
    "Simmer",
    "Boil",
    "Steam",
    "Poach",
    "Blanch",
    "Pressure cook",
    "Braise",
    "Smoke",
    "Sear",
    "Glaze",
    "Sous-vide",
    "Marinate",
    "Chill",
    "Freeze",
    "Defrost",
    "Ferment",
    "Caramelize",
    "Toast",
    "Infuse",
    "Reduce",
    "Whip",
    "Fold",
    "Knead",
    "Mix",
    "Blend",
    "Emulsify",
    "Froth",
    "Macerate",
    "Stir",
    "Heat",
    "Cook"
  ]
}