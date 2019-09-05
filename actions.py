__author__ = 'tomli'
import re
from fbchat.models import Message
import scrython
import random, json


def local_get_card(client, author_id, message_object, thread_id, thread_type):
        # if the message object has text

        if message_object.text:

            with open('ThreadConfigs.json', 'r+') as json_data:
                config = json.load(json_data)

            # begin text check
            card_find_list = None
            full_info = False
            card_price = False
            # card image
            if '!' in message_object.text:
                regex = '\!(.*?)\!'
                card_find_list = re.findall(regex, message_object.text)
            # card image and legality
            elif '?' in message_object.text:
                regex = '\?(.*?)\?'
                full_info = True
                card_find_list = re.findall(regex, message_object.text)
            # card price
            elif '$' in message_object.text:
                regex = '\$(.*?)\$'
                card_price = True
                card_find_list = re.findall(regex, message_object.text)

            if card_find_list:

                if alt_text_check(client, card_find_list, thread_id, thread_type):
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
                                        card = client.card_search(set_code[0], set_code[1])
                                        #scrython.cards.Named(fuzzy=set_code[0], set=set_code[1])
                                    else:
                                        print('not a code')
                                        # for set_name in scrython.Sets.name(set_code[1]):
                                        #     print(set_name)
                            except IndexError:
                                card = card_search(card_name)
                                # scrython.cards.Named(fuzzy=card_name)
                        else:
                            card = card_search(card_name)
                        # card = card.total_cards()
                        if type(card) is Exception:
                            if config[thread_id]['show_errors']:
                                client.send(Message(text=str(card)), thread_id=thread_id, thread_type=thread_type)
                        elif card == "None":
                            pass
                        else:
                            card_text = card.name()
                            if full_info:
                                card_text = ''.join('{0}- {1}\n'.format(key, val)
                                                    for key, val in card.legalities().items())
                            if card_price:
                                #card_text = card.name()
                                card_text += " - " + card.set_name()
                                card_text += " - $" + card.prices("usd")
                                print(card_text)
                                client.send(Message(text=card_text), thread_id=thread_id, thread_type=thread_type)
                            else:
                                # send card image with text
                                # check for card type to show all relavent images.
                                if card.layout() == 'normal' or card.layout() == 'split' \
                                        or card.layout() != 'transform':
                                    client.sendRemoteImage(card.image_uris()['normal'].split("?")[0], message=card_text,
                                                         thread_id=thread_id, thread_type=thread_type)
                                else:
                                    #transform cards
                                    if card.layout() == 'transform':
                                        for face in card.card_faces():
                                            #  print(face)
                                            client.sendRemoteImage(face["image_uris"]['normal'].split("?")[0], message=card_text,
                                                                 thread_id=thread_id, thread_type=thread_type)


def card_search(card_name, set_code=None):
        try:
            if set_code:
                card = scrython.cards.Named(fuzzy=card_name, set=set_code)
            else:
                card = scrython.cards.Named(fuzzy=card_name)
            return card
        except Exception as err:
            return err


def get_card_oracle_text(client, card_name, thread_id, thread_type):

        card = card_search(card_name)

        if type(card) is Exception or card is None:
            print('oracle text failed')
        else:
            card_text = 'Oracle Text For {} :\n {}'.format(card.name(), card.oracle_text())
            client.send(Message(text=card_text), thread_id=thread_id, thread_type=thread_type)

def alt_text_check(client, card_find_list, thread_id, thread_type):
    if card_find_list[0].lower() == 'help':
        client.send(Message(text='Use !card name! for card image, shows most recent printing \n'
                               'Use ?card name? for image and format legality\n'
                               'Use $ for price for the card in dollars\n'
                               'Use [3 char set code] for specific art/set\n'
                               'Use the WOW reaction on an image sent by me to get its oracle text'
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
        card_text = 'wait, that\'s not right'
        card = token_list[chosen_token]
        if card['name'].lower() == 'treasure':
            card_text = 'We found the Loot'

        client.sendRemoteImage(card['image_uris']['normal'].split("?")[0], message=Message(text='Searching Ixalan for Treasure...'),
                                                 thread_id=thread_id, thread_type=thread_type)
        client.send(Message(text=card_text), thread_id=thread_id, thread_type=thread_type)
        return False

    return True

def nickname_boxer_setting():
    pass