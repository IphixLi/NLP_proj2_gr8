import spacy
import re
nlp = spacy.load('en_core_web_sm')
spacy_model = spacy.load("en_core_web_lg")

def findTool(ListSentence):
    # Yifan: 
    # - Combine sugar, flour, and salt in a saucepan. (got "saucepan" and "pan")
    # - Preheat an air fryer to 400 degrees F (200 degrees C) according to manufacturer’s instructions. ([])
    toolList = []
    for i in range(len(ListSentence)):
        single = findToolSingle(imperative_to_normal(ListSentence[i]))
        if single == [] and i > 0:
            single = toolList[-1]
        toolList.append(single)
    return toolList

def findMethod(ListSentence):
    prime = []
    verbs = []
    for i in ListSentence:
        single1 = list(set(findRelationVerbSingle(imperative_to_normal(i))))
        single2 = list(set(findMethodSingle(imperative_to_normal(i))))
        prime.append(single2) 
        for j in single1:
            if j in tool_method_list["bad_verb"]:
                single1.remove(j)
            if j in single2:
                single1.remove(j)
        verbs.append(single1)
    return prime, verbs   

def answerVague(sen):
    # Yifan: fix bug: "Preheat the oven to 350 degrees F (175 degrees C)." (index1 = sen.index(item[0]) ValueError: substring not found)
    try:
        RelationList = findRelationVerbNoun(imperative_to_normal(sen))
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
    except:
        return [sen.lower()[:-1]]


#===================================================
# here is the supporting functions for above
#===================================================
#find tool
def findToolSingle(sentence):
    toolList = []
    sentence = sentence.lower()
    for i in tool_method_list["cooking_tools"]:
        if match_whole_word(sentence, i):
            toolList.append(i)
            if " " in i:
                j = i.replace(" ", "")
                sentence = sentence.replace(i, j)
    return toolList


#find primary cooking method
def findMethodSingle(sentence):
    methodllist = []
    sentence = sentence.lower()
    for i in tool_method_list["cooking_methods"]:
        if match_whole_word(sentence, i):
            methodllist.append(i)
    return methodllist


#find verb method 1
def findAllVerbSingle(sentence):
    doc = nlp(sentence)
    verbs = []
    for token in doc:
        if token.pos_ == "VERB" and not token.text.endswith("ed"):
            verbs.append(token.lemma_)
    return list(set(verbs))


#find verb method 2
def findRelationVerbSingle(sentence):
    verbs = []
    spacy_output = spacy_model(sentence)
    for n in spacy_output.noun_chunks:
        if n.text == "You":
            continue
        verb = find_most_related_verb(n)
        if verb is not None:
            verbs.append(verb.lemma_)
    return list(set(verbs))

#find verb noun relation
def findRelationVerbNoun(sentence):
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
        if sentence == '':
            return sentence
        if "," in sentence:
            i = sentence.index(",")
            if " " not in sentence[:i]:
                sentence = sentence[i+2 :]
        while sentence.startswith(" "):
            sentence = sentence[1:]
        if sentence.endswith("."):
            return f"You {sentence[0].lower()}{sentence[1:]}"
        else:
            return f"You {sentence[0].lower()}{sentence[1:]}."
    
    except Exception:
        return sentence



#keywordlist
tool_method_list = {
  "cooking_tools": [
    "cutting board",
    "mixing bowl",
    "measuring cup",
    "measuring spoon",    
    "wooden spoon",
    "slotted spoon",    
    "roasting pan",
    "baking sheet",
    "rolling pin",
    "pastry brush",
    "kitchen shears",
    "vegetable peeler",    
    "mixing spoon",
    "silicone spatula",
    "meat thermometer",    
    "oven mitts",
    "pot holder",
    "kitchen timer",
    "food processor",    
    "can opener",    
    "stand mixer",
    "hand mixer", 
    "pastry cutter",
    "mandoline slicer",
    "garlic press",
    "seafood crackers",    
    "air fryer",
    "mortar",
    "pestle",   
    "pot",
    "pan",
    "knife",
    "whisk",
    "spatula",
    "tong",
    "ladle",
    "skillet",
    "saucepan",
    "oven",
    "stockpot",
    "grater",
    "zester",
    "colander",
    "strainer",
    "blender",
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
        "continue",
        "start",
        "create",
        "accord",
        "work",
        "finish",
        "return"
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
    "pressure cook",
    "braise",
    "smoke",
    "marinate",
    "chill",
    "freeze",
    "ferment",
    "mix",
    "blend",
    "stir",
    "heat"
  ]
}
