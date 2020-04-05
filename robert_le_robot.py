import asyncio
import datetime
import json
import pydoc
import sys
from pprint import pprint

# community
from mattermostdriver import Driver
import yaml
from sympy.parsing.latex import parse_latex

# own
from classroom_api import retrieve_parse_works

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

# Globals

VERBOSE = True

# Files
PATH_TOKEN_BOT = "./config/token.robert"
PATH_OPTIONS_SERVER = "./config/config.yml"
PATH_ANSWER_HELP = './responses/help_reponse.md'
PATH_STANDARD_ANSWERS = './responses/standard_answers.yml'
PATH_TEAM_CLASSROOM = './config/team_classroom.yml'

# key words
START_COMMAND = "!robert "
START_LATEX = "```latex"
END_LATEX = "\n```"

# Formatting options
DATETIME_FORMAT = "La date est %Y-%m-%d et il est %H:%M"


def get_team_classroom():
    associations = read_yaml_file(PATH_TEAM_CLASSROOM)
    return associations


def read_yaml_file(path):
    with open(path, 'r') as stream:
        try:
            content_as_dict = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            if VERBOSE:
                print(repr(e))
            raise(e)
    return content_as_dict


def get_standard_answers():
    standard_answers = read_yaml_file(PATH_STANDARD_ANSWERS)
    return standard_answers


def read_token():
    '''
    retourne le token du bot depuis le fichier token
    '''
    with open(PATH_TOKEN_BOT) as f:
        token = f.read().strip()
    if VERBOSE:
        print(token)
    return token


def get_options():
    '''
    Lit les options depuis le fichier config.yml
    y ajoute le token et les retourne
    '''
    options = read_yaml_file(PATH_OPTIONS_SERVER)
    token = read_token()
    options["token"] = token
    return options


def create_driver(options=None):
    '''
    Retourne une instance de Driver qui permet d'envoyer des commandes
    au serveur
    '''
    if options is None:
        options = get_options()
    driver = Driver(options)
    return driver


def get_user(username, driver=None):
    '''Retourne les infos d'un utilisateur par son username'''
    if VERBOSE:
        print(f"\nget user {username}")
    if driver is None:
        driver = create_driver()
    user = driver.users.get_user_by_username(username)
    if VERBOSE:
        print(f"\nuser {username} is")
        print(user)
    return user


def get_channel_info_from_channel_id(channel_id, driver=None):
    if driver is None:
        driver = create_driver()
    driver.login()
    mattermost_answer = driver.channels.get_channel(channel_id)
    if VERBOSE:
        pprint(mattermost_answer)
    return mattermost_answer


def get_team_from_channel(channel_id, driver=None):
    mattermost_answer = get_channel_info_from_channel_id(channel_id,
                                                         driver=driver)
    team_id = mattermost_answer.get('team_id')
    return team_id


@asyncio.coroutine
def message_handler(message):
    '''traite un message et y répond via le bot'''
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
    parse_msg(msg_json)


def parse_msg(msg_json):
    '''
    traite le contenu json d'un message lu par le bot
    si c'est un post, il le traite
    '''
    if VERBOSE:
        print("\n###############################################\n")
        print("parse_msg")
    if 'data' in msg_json and 'post' in msg_json['data']:
        # it's a post message
        msg_json_data_post = msg_json['data']['post']
        team_id = msg_json['data'].get('team_id')
        parse_post(msg_json_data_post, team_id)


def parse_post(msg_json_data_post, team_id):
    '''
    extraie la commande lue par le bot, calcule la réponse et l'envoie
    on ne traite que les posts qui commencent par !robert ou ```latex
    '''
    if VERBOSE:
        print("\n###############################################\n")
        print("parse_post")

    if "message" in msg_json_data_post:
        message = json.loads(msg_json_data_post)
        channel_id = message.get("channel_id")
        message_content = message.get('message')
        if VERBOSE:
            print("message_content", message_content)
            print("team_id", team_id)

        deal_answer = False
        latex_syntax = False

        if message_content.startswith(START_COMMAND):
            commande = message_content.split(START_COMMAND)[1]
            if VERBOSE:
                print("\ncommande reçue")
                print(commande)
            deal_answer = True

        elif message_content.startswith(START_LATEX):
            commande = message_content.split(START_LATEX)[1].strip()
            commande = commande.split(END_LATEX)[0].strip()
            if VERBOSE:
                print("commande reçue  ", commande)
                print(commande)
            latex_syntax = True
            deal_answer = True

        if deal_answer:
            bot_replies(commande,
                        latex_syntax=latex_syntax,
                        channel_id=channel_id,
                        team_id=team_id)


def bot_replies(command, driver=None, latex_syntax=False,
                channel_id=None, team_id=None):
    '''crée la réponse texte du bot'''
    if VERBOSE:
        print("\n##############################################\n")
        print("bot_replies")
    if channel_id is not None:
        msg_options = bot_command_options(command,
                                          channel_id,
                                          team_id,
                                          latex_syntax=latex_syntax)

        if VERBOSE:
            print("\nmsg_options")
            pprint(msg_options)
        if driver is None:
            driver = create_driver()
        driver.login()
        driver.posts.create_post(msg_options)
        driver.logout()


def bot_command_options(command, channel_id, team_id, latex_syntax=False):
    '''choisit la bonne réaction et construit la réponse du bot'''
    if VERBOSE:
        print("\n##############################################\n")
        print("bot_command_options received", command)
    if 'travail' in command:
        if VERBOSE:
            print('command : travail !')
        last_param = command.split(' ')[-1]
        print("last_param")
        print(last_param)
        try:
            how_many = int(last_param)
        except ValueError as e:
            print(repr(e))
            how_many = 1
        if VERBOSE:
            print(how_many)
        associations_teams_classroom = get_team_classroom()

        print("team_id", team_id)

        if team_id is None or team_id == '':
            team_id = get_team_from_channel(channel_id)

        course_id = associations_teams_classroom.get(team_id)
        if course_id is not None:
            answer = retrieve_parse_works(how_many=how_many,
                                          course_id=course_id)
        else:
            answer = standard_answers["no_classroom"]
    elif command in ['help', 'aide']:
        with open(PATH_ANSWER_HELP) as f:
            answer = f.read()

    elif command in ["heure", "date", "aujourd'hui"]:
        answer = datetime_format_command()

    elif command.startswith("python"):
        help_seeked_on = command.split("python")[1].strip()
        answer = python_format_help(help_seeked_on)

    elif command.startswith("latex") or latex_syntax:
        if not latex_syntax:
            latex_command = command.split("latex")[1].strip()
        else:
            latex_command = command
        try:
            answer = latex_evaluate_command(latex_command)
        except Exception as e:
            answer = standard_answers['invalid_latex']

    else:
        answer = standard_answers["cannot_do"]

    options = {
        'channel_id': channel_id,
        'message': answer,
    }
    return options


def datetime_format_command():
    '''
    retourne l'heure formattée
    '''
    now = datetime.datetime.now()
    if VERBOSE:
        print("heure", now)
    answer = now.strftime(DATETIME_FORMAT)
    return answer


def python_format_help(help_seeked_on):
    '''
    retourne l'aide d'un module python formattée
    https://stackoverflow.com/questions/15133537/pydoc-render-doc-adds-characters-how-to-avoid-that
    '''
    if VERBOSE:
        print("help_seeked_on", help_seeked_on)
    try:
        answer = pydoc.render_doc(help_seeked_on,
                                  "Voici l'aide de **%s**",
                                  renderer=pydoc.plaintext)
    except ImportError as e:
        answer = f"Il n'y a pas d'aide pour **{help_seeked_on}**"
    return answer


def latex_evaluate_command(latex_command):
    '''
    tente d'évaluer une commande latex avec sympy
    https://docs.sympy.org/latest/modules/parsing.html
    '''
    if VERBOSE:
        print("latex command received", latex_command)

    parsed_expr = parse_latex(latex_command)

    try:
        answer = str(parsed_expr.evalf(4))
    except Exception as e:
        if VERBOSE:
            print(repr(e))
        answer = str(parsed_expr)
    if VERBOSE:
        print("latex reponse", answer)
    return answer


def robert_le_robot(verbose=False):
    global standard_answers
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
