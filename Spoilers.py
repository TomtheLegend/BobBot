
__author__ = 'tomli'

from fbchat import Client
from fbchat.models import *
import scrython
import json
import time
import datetime


def get_new_spoilers():
    lastList = []
    currentList = []
    savelist = []
    sets = []

    #Grab the data
    with open('Spoilers.json', 'r') as json_data:
        d = json.load(json_data)
        lastList = d["spoilers"]
        sets = d["sets"]

    #get spoilers sets and make the search query]
    #todo for loop over the sets, have sets as seperate json dicts.
    # have spoiler end dates and if it get to the date after then remove from list, post full spoiler list if ulr exists?
    query = ""
    for s in sets:
        if query is "":
            query = "++e:{}".format(s)
        else:
            query += " OR ++e:{}".format(s)

    spoilers = scrython.cards.Search(q=query, order='spoiled')
    # for card in reversed(spoilers.data()):
    #     print(card)

     #If the total cards has increased
    if spoilers.total_cards() > len(lastList):

        send_list = []
        #Iterate through data
        for card in reversed(spoilers.data()):
            savelist.append(card['name'])
            if card['name'] not in lastList:
                #add new cards to a list to send
                if card['layout'] == 'normal' or 'split':
                    send_list.append([card['name'], card['image_uris']['normal'].split("?")[0]])
                else:
                    #transform cards
                    if card['layout'] == 'transform':
                        for face in card['card_faces']:
                            send_list.append([card['name'], face['image_uris']['normal'].split("?")[0]])


        send_image(send_list)

        json_dict = {"spoilers": savelist,
                     "sets": sets}
        with open('Spoilers.json', 'w') as json_in:
            json.dump(json_dict, json_in)


def send_image(send_list):
    thread_type = ThreadType.GROUP

    with open('Settings.json', 'r') as json_data:
        d = json.load(json_data)
        cred_List = d["credentials"]

    client = Client(cred_List["email"], cred_List["password"])

    for new_card in send_list:
        message = "SPOILER ALERT  - " + new_card[0]
        # Will download the image at the url `<image url>`, and then send it
        client.sendRemoteImage(new_card[1], message=Message(text=message),
                               thread_id=cred_List["spoiler_thread"], thread_type=thread_type)

    client.logout()
    timestamp_text = "{0} - {1}".format(datetime.datetime.today(), message)
    print(timestamp_text)


def send_text(card):
    thread_type = ThreadType.GROUP

    with open('Settings.json', 'r') as json_data:
        d = json.load(json_data)
        cred_List = d["credentials"]

    client = Client(cred_List["email"], cred_List["password"])

    card_message = "{}\n{}".format(card['name'], card['oracle_text'])

    client.send(Message(text=card_message), thread_id=cred_List["spoiler_thread"], thread_type=thread_type)


def send_local_image(image, message):
    thread_type = ThreadType.GROUP

    with open('Settings.json', 'r') as json_data:
        d = json.load(json_data)
        cred_List = d["credentials"]

    client = Client(cred_List["email"], cred_List["password"])
    print(client.uid)

    # Will download the image at the url `<image url>`, and then send it
    client.sendLocalImage(image, message=Message(text=message),
                           thread_id=cred_List["spoiler_thread"], thread_type=thread_type)

    client.logout()
    timestamp_text = "{0} - {1}".format(datetime.datetime.today(), message)
    print(timestamp_text)





def april_fool():
    file_loc = 'D:/Programming/april fools/'
    fool_list = [['Urza\'s Tower', 'Urza\'s Tower.png'],
                 ['Unite the Gatewatch', 'Unite the Gatewatch.png'],
                 ['Colossal Dreadmaw', 'Colossal Dreadmaw.png']]

    for fool in fool_list:

        image_loc = file_loc + fool[1]
        print (image_loc)

        send_local_image(image_loc, "SPOILER ALERT  - " + fool[0])

        time.sleep(100)


while True:
    # '2018-09-21 09:00:00.00'
    if datetime.datetime.now() < datetime.datetime.strptime("19 Apr 19", "%d %b %y"):
        get_new_spoilers()

    time.sleep(300)
