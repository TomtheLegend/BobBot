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
            self.local_get_card(author_id, message_object, thread_id, thread_type)

    def local_get_card(self, author_id, message_object, thread_id, thread_type):
        if message_object.text:
            card_find_list = None
            full_info = False
            card_price = False
            if '!' in message_object.text:
                regex = '\!(.*?)\!'
                card_find_list = re.findall(regex, message_object.text)
            elif '?' in message_object.text:
                regex = '\?(.*?)\?'
                full_info = True
                card_find_list = re.findall(regex, message_object.text)
            elif '$' in message_object.text:
                regex = '\$(.*?)\$'
                card_price = True
                card_find_list = re.findall(regex, message_object.text)

            if card_find_list:
                if card_find_list[0].lower() == 'help':
                    self.send(Message(text='Use !card name! for card image \nUse ?card name? for image and legality\n'
                                           'Use [3 char set code] for specific art'), thread_id=thread_id, thread_type=thread_type)
                else:
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
                                        card = self.card_search(set_code[0], set_code[1])
                                            #scrython.cards.Named(fuzzy=set_code[0], set=set_code[1])
                                    else:
                                        print('not a code')
                                        # for set_name in scrython.Sets.name(set_code[1]):
                                        #     print(set_name)
                            except IndexError:
                                card = self.card_search(card_name)
                                    # scrython.cards.Named(fuzzy=card_name)
                        else:
                            card = self.card_search(card_name)
                        # card = card.total_cards()
                        print(type(card))
                        if type(card) is Exception:
                            if thread_id != '187068898324185':
                                self.send(Message(text=str(card)), thread_id=thread_id, thread_type=thread_type)
                        elif card == "None":
                            pass
                        else:
                            card_text = ""
                            if full_info:
                                card_text = ''.join('{0}- {1}\n'.format(key, val)
                                                    for key, val in card.legalities().items())
                            if card_price:
                                card_text = card.name()
                                card_text += " - " + card.set_name()
                                card_text += " - $" + card.currency("usd")
                                print(card_text)
                                self.send(Message(text=card_text), thread_id=thread_id, thread_type=thread_type)
                            else:
                                card_image = card.image_uris()['normal'].split("?")[0]
                                self.sendRemoteImage(card_image, message=Message(text=card_text),
                                                     thread_id=thread_id, thread_type=thread_type)



    def card_search(self, card_name, set_code=None):
        try:
            if set_code:
                card = scrython.cards.Named(fuzzy=card_name, set=set_code)
            else:
                card = scrython.cards.Named(fuzzy=card_name)
            return card
        except Exception as err:
            return err


    def prank_only_set_card(self, card_name,  author_id, message_object, thread_id, thread_type):
        card = scrython.cards.Named(fuzzy=card_name)
        card_image = card.image_uris()['normal'].split("?")[0]
        self.sendRemoteImage(card_image, message=Message(text=''),
                             thread_id=thread_id, thread_type=thread_type)


with open('Settings.json', 'r') as json_data:
    d = json.load(json_data)
    cred_List = d["credentials"]

client = CardFetch(cred_List["email"], cred_List["password"])
client.listen()
