import asyncio
import json

from datetime import datetime
from datetime import timedelta
from pprint import pprint

# own

from constants import VERBOSE
from constants import DEFAULT_MUTE_DURATION

from mattermost_api import driver_create_login_get_info
from mattermost_api import get_all_channels

from logging_system import logger

from utils import write_to_file
from utils import read_from_file

from post import Post


__title__ = '''Robert le robot'''
__author__ = '''qkzk'''
__date__ = '''2020/04/04'''
__doc__ = '''
titre:   {0}
author:  {1}
date:    {2}

Robert le robot est un bot Mattermost qui utilise Python et la librairie
mattermostdriver pour communiquer avec mon serveur.

Le bot se connecte à mattermost avec un compte de bot.
Ensuite il crée un webhook qui réagit aux messages qu'il peut lire.

Chaque message passant sur le channel est lu puis traité par le bot.

A l'heure actuelle il peut :

* afficher de l'aide,
* afficher l'heure,
* afficher l'aide d'une fonction python
* tenter d'évaluer une expression latex
'''.format(__title__, __author__, __date__)


class Robert:
    def __init__(self):
        self.logger = logger
        self.__state = {}
        self.__driver, self.__id, self.__username = driver_create_login_get_info()
        self.logger.info("init websocket")
        self.channel_ids = get_all_channels()
        self.channel_mode = self.default_mode()

        if VERBOSE:
            print("\n###############################################\n")
            print("start async message_handler")
        self.__driver.init_websocket(self.__message_handler)

    def get_driver(self):
        return self.__driver

    def id(self):
        return self.__id

    def username(self):
        return self.__username

    def channels():
        return self.__channel_ids

    def get_state(self):
        return self.__state

    def set_state(self, state):
        self.__state = state

    def get_state_for_user(self, user_id):
        if VERBOSE:
            print("\nRobert : state asked")
        return self.__state.get(user_id)

    def set_state_for_user(self, user_id, state):
        self.__state[user_id] = state

    def delete_state_for_user(self, user_id):
        if user_id in self.__state:
            if VERBOSE:
                print("\nRobert : state deleted for", user_id)
                print(self.__state)
            del self.__state[user_id]

    def validation(self, user_id):
        if user_id in self.__state:
            command = self.__state[user_id]
            post = Post(self, None, None)
            post.reply(command,
                       sender_user_id=user_id,
                       channel_id=channel_id)
            self.delete_state_for_user(user_id)

    def __default_channel_mode(id, channel_id):
        return {
            "channel_id": channel_id,
            "muted": False,
        }

    def default_mode(self):
        return {
            channel_id: self.__default_channel_mode(channel_id)
            for channel_id in self.channel_ids
        }

    def set_channel_mode(self, channel_id, mute_status, param=None):
        next_mode = {
            "channel_id": channel_id,
            "mute": mute_status,
        }
        if param is not None:
            next_mode = dict(next_mode, **param)
        self.channel_mode[channel_id] = next_mode

    def get_channel_mode(self, channel_id):
        return self.channel_mode.get(channel_id)

    @asyncio.coroutine
    def __message_handler(self, message):
        '''traite un message et y répond via le bot'''
        if VERBOSE:
            print("\nmy_event_handler")
            print("\n###############################################\n")
        msg_json = json.loads(message)
        if VERBOSE:
            print("\nmessage_content")
            pprint(msg_json)
            print("\n###############################################\n")
        self.__post_obj = Post.from_json(self, msg_json)
        if self.__post_obj is not None:
            self.__post_obj.parse_post()


if __name__ == '__main__':
    Robert()
