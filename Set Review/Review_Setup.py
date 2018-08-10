__author__ = 'tomli'


import scrython
import json


def main():

    #Grab the data
    with open('review.json', 'r') as json_data:
        d = json.load(json_data)
        set = d["set"]


    command = "e:{}".format(set)
    all_type = scrython.cards.Search(q=command)
    types = []
    for card in all_type.data():
        card = card["type_line"].replace("—", "").replace("/", "").split()
        for c in card:
            if c not in types:
                types.append(c)

    types = sorted(types)
    print(types)

    json_dict = {"set": set,
                "types": types}
    with open('review.json', 'w') as json_in:
        json.dump(json_dict, json_in)



main()