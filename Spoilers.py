
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

    #Grab the data
    with open('Spoilers.json', 'r') as json_data:
        d = json.load(json_data)
        lastList = d["spoilers"]

    spoilers = scrython.cards.Search(q="++e:{}".format("DOM"), order='spoiled')
    for card in reversed(spoilers.data()):
        print(card)

     #If the total cards has increased
    if spoilers.total_cards() > len(lastList):

        #Iterate through data
        for card in reversed(spoilers.data()):
            savelist.append(card['name'])
            if card['name'] in lastList:
                continue
            # send the card to facebook
            card_text = "SPOILER ALERT  - {}".format(card['name'])
            #send_image(card['image_uris']['normal'].split("?")[0], card_text)
            # send_image(card['image_uris']['normal'], card['name'])

        json_dict = {"spoilers": savelist}
        with open('Spoilers.json', 'w') as json_in:
            json.dump(json_dict, json_in)


def send_image(image, message):
    thread_type = ThreadType.GROUP

    with open('Spoilers.json', 'r') as json_data:
        d = json.load(json_data)
        cred_List = d["credentials"]

    client = Client(cred_List["email"], cred_List["password"])

    # Will download the image at the url `<image url>`, and then send it
    client.sendRemoteImage(image, message=Message(text=message),
                           thread_id=cred_List["spoiler_thread"], thread_type=thread_type)

    client.logout()
    timestamp_text = "{0} - {1}".format(datetime.datetime.today(), message)
    print(timestamp_text)

while True:
    get_new_spoilers()
    time.sleep(300)

