__author__ = 'tom lievesley'

__author__ = 'tom lievesley'


from fbchat import log, Client
from fbchat.models import *
import scrython
import re
import datetime
import json
import random


# Subclass fbchat.Client and override required methods
class CardFetch(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(author_id, thread_id)
        self.markAsRead(author_id)

        if author_id != self.uid:
            self.local_get_card(author_id, message_object, thread_id, thread_type)


    def local_get_card(self, author_id, message_object, thread_id, thread_type):
        if message_object.text:
            # begin text check
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

                if self.alt_text_check(card_find_list, author_id, message_object, thread_id, thread_type):
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
                                # send card image with text
                                # check for card type to show all relavent images.
                                if card.layout() == 'normal' or card.layout() == 'split':
                                    self.sendRemoteImage(card.image_uris()['normal'].split("?")[0], message=card_text,
                                                         thread_id=thread_id, thread_type=thread_type)
                                else:
                                    #transform cards
                                    if card.layout() == 'transform':
                                        for face in card.card_faces():
                                            print(face)
                                            self.sendRemoteImage(face["image_uris"]['normal'].split("?")[0], message=card_text,
                                                                 thread_id=thread_id, thread_type=thread_type)



    def alt_text_check(self,card_find_list, author_id, message_object, thread_id, thread_type):
        if card_find_list[0].lower() == 'help':
            self.send(Message(text='Use !card name! for card image, shows most recent printing \n'
                                   'Use ?card name? for image and format legality\n'
                                   'Use $ for price for the card in dollars\n'
                                   'Use [3 char set code] for specific art/set\n'
                                   'examples:\n'
                                   '?dark confident?\n'
                                   '!dark confident[rav]!\n'
                                   '$dark confident[rav]$'), thread_id=thread_id, thread_type=thread_type)
            return False

        if card_find_list[0].lower() == 'treasure':
            search = scrython.cards.Search(q="++is:token set:txln")
            token_list = search.data()
            token_list_len = len(token_list)-1
            chosen_token = random.randint(0, token_list_len)
            card_text = 'wait, thats not right'
            card = token_list[chosen_token]
            if card['name'].lower() == 'treasure':
                card_text = 'We found the Loot'

            self.sendRemoteImage(card['image_uris']['normal'].split("?")[0], message=Message(text='Searching Ixalan for Treasure...'),
                                                     thread_id=thread_id, thread_type=thread_type)
            self.send(Message(text=card_text), thread_id=thread_id, thread_type=thread_type)
            return False

        return True


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
