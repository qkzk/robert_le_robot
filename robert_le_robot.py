import asyncio
import datetime
import json
import pydoc
import sys
from pprint import pprint

# community
from mattermostdriver import Driver
# import yaml
from sympy.parsing.latex import parse_latex

# own

from reply import get_standard_answers
from get_format_sessions import get_format_sessions
from mattermost_api import read_token, get_options, create_driver
from post import Post
from reply import Reply

from constants import VERBOSE
from constants import PATH_TOKEN_BOT
from constants import PATH_OPTIONS_SERVER
from constants import PATH_ANSWER_HELP
from constants import PATH_STANDARD_ANSWERS
from constants import PATH_TEAM_CLASSROOM
from constants import START_COMMAND
from constants import START_LATEX
from constants import END_LATEX
from constants import DATETIME_FORMAT

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
driver = None


@asyncio.coroutine
def message_handler(message):
    '''traite un message et y répond via le bot'''
    global driver
    if VERBOSE:
        print("\nmy_event_handler")
        print("\n###############################################\n")
        print("\nmessage_content")
        print(message)
        print("\njsonify")
    msg_json = json.loads(message)
    if VERBOSE:
        pprint(msg_json)
        print("\n###############################################\n")
    # parse_msg(msg_json)
    if driver is None:
        print("\nMessage handler doesn't have a driver !\n")
    post_obj = Post.from_json(msg_json, driver)
    if post_obj is not None:
        post_obj.parse_post()


def robert_le_robot(verbose=False):
    global standard_answers
    global driver
    standard_answers = get_standard_answers()
    if VERBOSE:
        print("Launching robert_le_robot.py")
        print("\n##############################################\n")
        print("create_driver")
    driver = create_driver()
    if VERBOSE:
        print("\n##############################################\n")
        print("login")
    driver.login()
    # if VERBOSE:print("\n###############################################\n")
    # get_user("quentin", driver=driver)
    # get_user("qkzk", driver=driver)
    if VERBOSE:
        print("\n###############################################\n")
        print("start async message_handler")
    driver.init_websocket(message_handler)


if __name__ == '__main__':
    robert_le_robot()
