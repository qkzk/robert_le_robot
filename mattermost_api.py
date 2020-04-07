from pprint import pprint

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
from utils import get_standard_answers
from utils import read_yaml_file
from mattermostdriver import Driver


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
