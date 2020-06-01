__author__ = 'tom lievesley'


from fbchat import log, Client
from fbchat.models import *

import json
from json import JSONDecodeError

import actions
from os import path

# Subclass fbchat.Client and override required methods


class CardFetch(Client):
    def onReactionAdded(
        self,
        mid=None,
        reaction=None,
        author_id=None,
        thread_id=None,
        thread_type=None,
        ts=None,
        msg=None,
    ):

        message_emoted = self.fetchMessageInfo(mid, thread_id)
        if message_emoted.author ==self.uid:
            if reaction == MessageReaction.WOW:
                card_name = message_emoted.text.replace("SPOILER ALERT - ", "")
                card_name = card_name.replace("SPOILER ALERT  - ", "")
                print(card_name)
                actions.get_card_oracle_text(self, card_name, thread_id, thread_type)

    def onMessageSeen(self, **kwargs):
        pass

    def onMessage(self, mid=None,
                  author_id=None,
                  message=None,
                  message_object=None,
                  thread_id=None,
                  thread_type=ThreadType.USER,
                  ts=None,
                  metadata=None,
                  msg=None):

        self.markAsDelivered(author_id, thread_id)

        if author_id != self.uid:
            actions.local_get_card(self, author_id, message_object, thread_id, thread_type)

    def onPeopleAdded(
        self,
        mid=None,
        added_ids=None,
        author_id=None,
        thread_id=None,
        ts=None,
        msg=None
        ):
        """
        When a new person is added to a chat, show them a welcome message and show help.
        """
        thread_info = self.fetchThreadInfo(thread_id)
        actions.alt_text_check(client, ['help'], thread_id, thread_info.thread_type)

    def onEmojiChange(
        self,
        mid=None,
        author_id=None,
        new_emoji=None,
        thread_id=None,
        thread_type=ThreadType.USER,
        ts=None,
        metadata=None,
        msg=None,
    ):
        if author_id != self.uid:
            with open('ThreadConfigs.json', 'r+') as json_data:
                config = json.load(json_data)

            if thread_id in config:
                if config[thread_id]['emoji_change_allowed'] is False:
                    #print(config[thread_id]['emoji'])
                    self.changeThreadEmoji(config[thread_id]['emoji'], thread_id)

    def onNicknameChange(
        self,
        mid=None,
        author_id=None,
        changed_for=None,
        new_nickname=None,
        thread_id=None,
        thread_type=ThreadType.USER,
        ts=None,
        metadata=None,
        msg=None,
    ):
        if author_id != self.uid:
            with open('ThreadConfigs.json', 'r+') as json_data:
                config = json.load(json_data)

            if thread_id in config:
                if config[thread_id]['nicknames'] == 'boxer':
                    user_to_update = self.fetchUserInfo(changed_for)
                    new_nick = '{} \"{}\" {}'.format(user_to_update.first_name,
                                                     new_nickname,
                                                     user_to_update.last_name)
                    self.changeNickname(new_nick, changed_for, thread_id, thread_type)


def message_all_threads(client, message):
    threads = client.fetchThreadList()
    for thread in threads:
        print(thread)
        #client.send(Message(text=message), thread_id=thread.uid, thread_type=thread.type)


def all_threads_config(client):
    try:
        with open('ThreadConfigs.json', 'r+') as json_data:
            config = json.load(json_data)
    except FileNotFoundError:
        config = {}

    new_config = {}
    threads = client.fetchThreadList()
    for thread in threads:
        if thread.uid in config:
            new_config[thread.uid] = config[thread.uid]
        else:
            new_config[thread.uid] = {
                                        'thread_name': '',
                                        'show_errors': False,
                                        'emoji_change_allowed': True,
                                        'emoji': None,
                                        'nicknames': None,
                                        'show_spoilers': False,
                                        'april_fools': False
                                    }
            new_config[thread.uid]['thread_name'] = thread.name
    actions.config = new_config
    with open('ThreadConfigs.json', 'w') as save:
        json.dump(new_config, save, indent=4)


if __name__ =='__main__':
    try:
        with open('Settings.json', 'r') as json_data:
            d = json.load(json_data)
            cred_List = d["credentials"]
    except OSError:
        try:
            with open('/run/secrets/bobsettings', 'r') as json_data:
                d = json.load(json_data)
                cred_List = d["credentials"]
        except OSError:
            exit("Failed to load settings file.")
        except JSONDecodeError:
            exit("Json failed to decode the settings file.")
    # use session cookies to ensure not locked out.

    cookies = {}
    try:
        # Load the session cookies
        with open('session.json', 'r') as f:
            cookies = json.load(f)
    except OSError:
        # If it fails, never mind, we'll just login again
        pass

    actions.host = cred_List["host"]
    client = CardFetch(cred_List["email"], cred_List["password"],  session_cookies=cookies)
    # client = CardFetch(cred_List["email"], cred_List["password"],  session_cookies=cookies, logging_level=logging.DEBUG)

    all_threads_config(client)
    #
    # # Save the session again
    with open('session.json', 'w') as f:
        json.dump(client.getSession(), f)


    # message = 'Maintenance Alert: I will be going offline for maintenance, ' \
    #           'another message will be posted when back online. ' \
    #           'This is an automated message.'
    # message_all_threads(client, message)

    # listen for messages etc.
    client.listen()


