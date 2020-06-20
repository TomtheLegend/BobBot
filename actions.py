__author__ = 'tomli'
import re
from fbchat.models import Message
import scrython
import random, json
import urllib.request
from PIL import Image
import upsidedown
from fbchat import ThreadType


config = {}
host = ''


def local_get_card(client, author_id, message_object, thread_id, thread_type):
    # if the message object has text

        if message_object.text:
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
                if alt_text_check(client, card_find_list, thread_id, thread_type, author_id):
                    for card_name in card_find_list:
                        card = None
                        if "[" in card_name:
                            try:
                                regex = '(.*?)\[(.*?)\]'
                                set_code = re.findall(regex, card_name)
                                set_code = set_code[0]
                                # print(str(set_code))
                                if set_code[1]:
                                    # print(set_code[1])
                                    if len(set_code[1]) == 3:
                                        card = client.card_search(set_code[0], set_code[1])
                                        # scrython.cards.Named(fuzzy=set_code[0], set=set_code[1])
                                    else:
                                        print('not a code')
                            except IndexError:
                                card = card_search(card_name)
                                # scrython.cards.Named(fuzzy=card_name)
                        else:
                            card = card_search(card_name)
                        # card = card.total_cards()
                        # print(type(card))
                        if type(card) is scrython.ScryfallError:
                            if config[thread_id]['show_errors']:
                                client.send(Message(text=str(card)), thread_id=thread_id, thread_type=thread_type)
                        elif type(card) == scrython.cards.named.Named:
                            card_text = card.name()

                            if full_info:
                                card_text = ''.join('{0}- {1}\n'.format(key, val)
                                                    for key, val in card.legalities().items())
                            if card_price:
                                # card_text = card.name()
                                card_text += " - " + card.set_name()
                                card_text += " - $" + card.prices("usd")
                                print(card_text)
                                client.send(Message(text=card_text), thread_id=thread_id, thread_type=thread_type)
                            else:
                                # send card image with text
                                # check for card type to show all relavent images.
                                if card.layout() == 'normal' or card.layout() == 'split' \
                                        or card.layout() != 'transform':
                                    if config[thread_id]['april_fools']:
                                        flip_card(card.image_uris()['normal'].split("?")[0], client,
                                                  message=card_text,
                                                  thread_id=thread_id, thread_type=thread_type)
                                    else:
                                        card_image = card.image_uris()['normal'].split("?")[0]
                                        client.sendRemoteFiles(card_image, message=card_text,
                                                               thread_id=thread_id, thread_type=thread_type)
                                else:
                                    # transform cards
                                    if card.layout() == 'transform':
                                        for face in card.card_faces():
                                            # print(face)
                                            if config[thread_id]['april_fools']:
                                                flip_card(face["image_uris"]['normal'].split("?")[0], client,
                                                          message=card_text,
                                                          thread_id=thread_id, thread_type=thread_type)
                                            else:
                                                card_image = face["image_uris"]['normal'].split("?")[0]
                                                client.sendRemoteFiles(card_image, message=card_text,
                                                                       thread_id=thread_id, thread_type=thread_type)


def card_search(card_name, set_code=None):
    try:
        if set_code:
            card = scrython.cards.Named(fuzzy=card_name, set=set_code)
        else:
            card = scrython.cards.Named(fuzzy=card_name)
        # print(card)
        # if type(card) is scrython.cards.cardid.CardsObject:
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


def alt_text_check(client, card_find_list, thread_id, thread_type, author_id):
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
    # admin commands
    if thread_type == ThreadType.GROUP:
        group = client.fetchGroupInfo(thread_id)
        if author_id in group[thread_id].admins:
            return admin_settings(client, card_find_list, thread_id, thread_type, author_id)
    else:
        if config[thread_id]['thread_name'] == host:
            return host_options(client, card_find_list, thread_id, thread_type)
        else:
            return admin_settings(client, card_find_list, thread_id, thread_type, author_id)

    return True


def admin_settings(client, card_find_list, thread_id, thread_type, author_id):
    if card_find_list[0].lower() == 'admin help':
        client.send(Message(text='admin show errors \n'
                                 'admin april fools'),
                    thread_id=thread_id,
                    thread_type=thread_type)
        return False
    elif card_find_list[0].lower() == 'admin show errors':
        thread_config_change_bool(client, thread_id, thread_id, thread_type, 'show_errors')
        return False
    elif card_find_list[0].lower() == 'admin april fools':
        thread_config_change_bool(client, thread_id, thread_id, thread_type, 'april_fools')
        return False

    return True


def host_options(client, card_find_list, thread_id, thread_type):
    if card_find_list[0].lower() == 'host show groups':
        message_text = "\n".join(str(value['thread_name']) for key, value in config.items())
        client.send(Message(text=message_text),
                    thread_id=thread_id,
                    thread_type=thread_type)
        return False
    elif 'host send message' in card_find_list[0].lower():
        message_id = card_find_list[0].lower().split('host send message')[1].strip()
        thread_list = client.fetchThreadList()
        for thread in thread_list:
            send_custom_message(client, thread.uid, thread.type, message_id)
    elif "host show errors" in card_find_list[0].lower():
        thread_name = card_find_list[0].lower().split('host show errors')[1].strip()
        host_update_thread(client, thread_id, thread_type, thread_name, "show_errors")
        return False
    elif "host april fools" in card_find_list[0].lower():
        thread_name = card_find_list[0].lower().split('host april fools')[1].strip()
        host_update_thread(client, thread_id, thread_type, thread_name, "april_fools")
        return False

    return True


def send_custom_message(client, thread_id, thread_type, message_id):
    message_text = ''
    with open('messages.json', 'r') as json_data:
        d = json.load(json_data)
        message_text = d["messages"]
    if message_id in message_text.keys():
        message_text = message_text[message_id]
        message_text += '\nThis is an automated message.'
        print("# text: {}\nthread: {}\ntype: {}\n".format(message_text, str(thread_id), str(thread_type)))
        client.send(Message(text=message_text),
                    thread_id=thread_id,
                    thread_type=thread_type)


def host_update_thread(client, thread_id, thread_type, thread_name, key_name):
    chat_id = [key for key, info in config.items() if info["thread_name"].lower() == thread_name.lower()]
    print(chat_id)
    if len(chat_id) > 0:
        thread_config_change_bool(client, chat_id[0], thread_id, thread_type, key_name)


def thread_config_change_bool(client, thread_id, message_thread_id, message_thread_type, key):
    config[thread_id][key] = not config[thread_id][key]
    send_text = '{} setting has been set to {}'.format(key, config[thread_id][key])
    client.send(Message(text=send_text),
                thread_id=message_thread_id,
                thread_type=message_thread_type)


def nickname_boxer_setting():
    pass


def flip_card(card_image_url, client, message, thread_id, thread_type):
    # save it
    urllib.request.urlretrieve(card_image_url, "local-filename.jpg")
    # flip it
    im = Image.open("local-filename.jpg")
    im = im.rotate(180)
    im.save("local-filename.jpg")
    # flip text
    message_mirror = upsidedown.transform(message)
    # send message
    client.sendLocalFiles("local-filename.jpg", message=message_mirror,
                          thread_id=thread_id, thread_type=thread_type)

