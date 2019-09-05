
__author__ = 'tomli'

from fbchat import Client
from fbchat.models import *
import scrython
import json
import time
import datetime


def get_new_spoilers(client):
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

        split_send_list = [send_list[x:x+10] for x in range(0, len(send_list), 10)]

        for chunk_list in split_send_list:
            send_image(client, chunk_list)
            time.sleep(5)

        json_dict = {"spoilers": savelist,
                     "sets": sets}
        with open('Spoilers.json', 'w') as json_in:
            json.dump(json_dict, json_in)
        print("Spoilers checked")

def send_image(client, send_list):

    with open('ThreadConfigs.json', 'r+') as json_data:
                config = json.load(json_data)

    for threadid, data in config.items():
        if data['show_spoilers']:
            #try:
                _thread = client.fetchThreadInfo(threadid)
                if _thread:
                    _threadtype = _thread[threadid].type
                    for new_card in send_list:
                        message = "SPOILER ALERT  - " + new_card[0]
                        print(new_card[0])
                        # Will download the image at the url `<image url>`, and then send it
                        # client.sendRemoteImage(new_card[1], message=Message(text=message),
                        #                        thread_id=threadid, thread_type=_threadtype)

                        client.sendRemoteFiles(new_card[1], message=Message(text=message),
                                               thread_id=threadid, thread_type=_threadtype)
            # except:
            #     pass
    timestamp_text = "{0}".format(datetime.datetime.today())
    print(timestamp_text)


def send_text(card):
    thread_type = ThreadType.GROUP

    with open('Settings.json', 'r') as json_data:
        d = json.load(json_data)
        cred_List = d["credentials"]

    client = Client(cred_List["email"], cred_List["password"])

    card_message = "{}\n{}".format(card['name'], card['oracle_text'])

    client.send(Message(text=card_message), thread_id=cred_List["spoiler_thread"], thread_type=thread_type)



if __name__ == '__main__':

    with open('Settings.json', 'r') as json_data:
        d = json.load(json_data)
        cred_List = d["credentials"]

    cookies = {}
    try:
        # Load the session cookies
        with open('spoilersession.json', 'r') as f:
            cookies = json.load(f)
    except:
        # If it fails, never mind, we'll just login again
        pass

    client = Client(cred_List["email"], cred_List["password"],  session_cookies=cookies)
    #client = CardFetch(cred_List["email"], cred_List["password"],  session_cookies=cookies, logging_level=logging.DEBUG)

    # Save the session again
    with open('spoilersession.json', 'w') as f:
        json.dump(client.getSession(), f)

    while True:

        # '2018-09-21 09:00:00.00'
        #if datetime.datetime.now() < datetime.datetime.strptime("19 Apr 19", "%d %b %y"):
        get_new_spoilers(client)

        time.sleep(300)
