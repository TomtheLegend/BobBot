__author__ = 'tomli'


from fbchat import log, Client
from fbchat.models import *
import scrython
import re
import datetime
import json



# Subclass fbchat.Client and override required methods
class CardFetch(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(author_id, thread_id)
        self.markAsRead(author_id)

        if author_id != self.uid:
            print(message_object.author)
            day = datetime.datetime.now().strftime("%d")
            month = datetime.datetime.now().strftime("%m")
            if day == "01" and month == "04":
                card_find_list = None
                if message_object.text:
                    if '!' in message_object.text:
                        regex = '\!(.*?)\!'
                        card_find_list = re.findall(regex, message_object.text)
                    if '?' in message_object.text:
                        regex = '\?(.*?)\?'
                        full_info = True
                        card_find_list = re.findall(regex, message_object.text)

                    if card_find_list:
                        # dave b
                        if message_object.author == "723551715":
                            self.prank_only_set_card("Bronze Sable", author_id, message_object, thread_id, thread_type)
                        # reece
                        elif message_object.author == "100000014705276":
                            self.prank_only_set_card("Torpor Orb", author_id, message_object, thread_id, thread_type)
                        # Mike
                        elif message_object.author == "587626850":
                            self.prank_only_set_card("Hot Fix", author_id, message_object, thread_id, thread_type)
                        # Simon
                        elif message_object.author == "100006607869682":
                            self.prank_only_set_card("Old Fogey", author_id, message_object, thread_id, thread_type)
                        # adam
                        elif message_object.author == "511000757":
                            self.prank_only_set_card("Ichorid", author_id, message_object, thread_id, thread_type)
                        # scott y
                        elif message_object.author == "599754537":
                            self.prank_only_set_card("Molten Rain", author_id, message_object, thread_id, thread_type)
                        # scott c
                        elif message_object.author == "100000843116991":
                            self.prank_only_set_card("storm crow", author_id, message_object, thread_id, thread_type)
                        else:
                            self.prank_only_set_card("counterspell", author_id, message_object, thread_id, thread_type)
            else:
                self.local_get_card(author_id, message_object, thread_id, thread_type)

    def local_get_card(self, author_id, message_object, thread_id, thread_type):
        if message_object.text:
                full_info = False
                if '!' in message_object.text:
                    regex = '\!(.*?)\!'
                    card_find_list = re.findall(regex, message_object.text)
                if '?' in message_object.text:
                    regex = '\?(.*?)\?'
                    full_info = True
                    card_find_list = re.findall(regex, message_object.text)

                if card_find_list:
                    for card_name in card_find_list:
                        card = None
                        if "[" in card_name:
                            try:
                                regex = '(.*?)\[(.*?)\]'
                                set_code = re.findall(regex, card_name)
                                set_code = set_code[0]
                                print(str(set_code))
                                if set_code[1]:
                                    print(set_code[1])
                                    if len(set_code[1]) == 3:
                                        card = scrython.cards.Named(fuzzy=set_code[0], set=set_code[1])
                                    else:
                                        print('not a code')
                                        # for set_name in scrython.Sets.name(set_code[1]):
                                        #     print(set_name)
                            except IndexError:
                                card = scrython.cards.Named(fuzzy=card_name)
                        else:
                            card = scrython.cards.Named(fuzzy=card_name)
                        # card = card.total_cards()
                        card_text = ""
                        if full_info:
                            card_text = ''.join('{0}- {1}\n'.format(key, val)
                                                for key, val in card.legalities().items())

                        card_image = card.image_uris()['normal'].split("?")[0]
                        self.sendRemoteImage(card_image, message=Message(text=card_text),
                                             thread_id=thread_id, thread_type=thread_type)



    def prank_only_set_card(self, card_name,  author_id, message_object, thread_id, thread_type):
        card = scrython.cards.Named(fuzzy=card_name)
        card_image = card.image_uris()['normal'].split("?")[0]
        self.sendRemoteImage(card_image, message=Message(text=''),
                             thread_id=thread_id, thread_type=thread_type)


with open('Spoilers.json', 'r') as json_data:
    d = json.load(json_data)
    cred_List = d["credentials"]

client = CardFetch(cred_List["email"], cred_List["password"])
client.listen()
