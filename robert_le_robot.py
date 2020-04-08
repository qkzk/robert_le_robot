import asyncio
import json
from pprint import pprint

# own

from constants import VERBOSE
from constants import PATH_ID_BOT

from mattermost_api import create_driver
from mattermost_api import driver_create_login_get_info

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
        self.__driver, bot_id, bot_username = driver_create_login_get_info()
        self.__state = {}
        saved_bot_id = read_from_file(PATH_ID_BOT)
        if VERBOSE:
            print("saved id", saved_bot_id)
            print("received id", bot_id)
            print("saved id doesn't match, updating")
        write_to_file(PATH_ID_BOT, bot_id)

        if VERBOSE:
            print("\n###############################################\n")
            print("start async message_handler")
        self.__driver.init_websocket(self.__message_handler)

    def get_driver(self):
        return self.__driver

    def get_state(self):
        return self.__state

    def set_state(self, state):
        self.__state = state

    def get_state_for_user(self, user_id):
        return self.__state.get(user_id)

    def set_state_for_user(self, user_id, state):
        self.__state[user_id] = state

    def await_confirmation(self, user_id, command):
        self.__state[user_id] = command

    def delete_state_for_user(self, user_id):
        if user_id in self.__state:
            del self.__state[user_id]

    def validation(self, user_id):
        if user_id in self.__state:
            command = self.__state[user_id]
            post = Post(self, True, None, None)
            post.reply(command,
                       sender_user_id=user_id,
                       channel_id=channel_id)
            self.delete_state_for_user(user_id)

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
            # exit()
        self.__post_obj = Post.from_json(self, msg_json)
        if self.__post_obj is not None:
            self.__post_obj.parse_post()


if __name__ == '__main__':
    robert = Robert()
