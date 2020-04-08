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


@asyncio.coroutine
def message_handler(message):
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
    post_obj = Post.from_json(msg_json)
    if post_obj is not None:
        post_obj.parse_post()


def robert_le_robot(verbose=False):
    # global driver
    if VERBOSE:
        print("Launching robert_le_robot.py")
        print("\n##############################################\n")
        print("create_driver")
    driver, bot_id, bot_username = driver_create_login_get_info()
    saved_bot_id = read_from_file(PATH_ID_BOT)
    if VERBOSE:
        print("received id", bot_id)
        print("saved id", saved_bot_id)
    if saved_bot_id != bot_id:
        if VERBOSE:
            print("saved id doesn't match")
        write_to_file(PATH_ID_BOT, bot_id)

    if VERBOSE:
        print("\n##############################################\n")
        print("login")
    if VERBOSE:
        print("\n###############################################\n")
        print("start async message_handler")
    driver.init_websocket(message_handler)


if __name__ == '__main__':
    robert_le_robot()
