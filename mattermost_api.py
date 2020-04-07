from pprint import pprint

from constants import VERBOSE
from constants import PATH_TOKEN_BOT
from constants import PATH_OPTIONS_SERVER
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
    driver.login()
    user = driver.users.get_user_by_username(username)
    if VERBOSE:
        print(f"\nuser {username} is")
        print(user)
    return user


def get_user_by_id(user_id, driver=None):
    '''Retourne les infos d'un utilisateur par son user_id'''
    assert type(user_id) == str, "get_user_id: user id is not a string"
    if VERBOSE:
        print(f"\nget user {user_id}")
    if driver is None:
        driver = create_driver()
    driver.login()
    user = driver.users.get_user(user_id)
    if VERBOSE:
        print(f"\nuser {user_id} is")
        print(user)
    return user


def get_channel_info_from_channel_id(channel_id, driver=None):
    if driver is None:
        driver = create_driver()
    driver.login()
    channel_info = driver.channels.get_channel(channel_id)
    if VERBOSE:
        pprint(channel_info)
    return channel_info


def get_team_from_channel(channel_id, driver=None):
    mattermost_answer = get_channel_info_from_channel_id(channel_id,
                                                         driver=driver)
    team_id = mattermost_answer.get('team_id')
    return team_id


def get_user_sessions_from_api(user_id, driver=None):
    if driver is None:
        driver = create_driver()
    driver.login()
    sessions = driver.users.get_user_sessions(user_id)
    if VERBOSE:
        pprint(sessions)
    return sessions


def get_user_audits_from_api(user_id, driver=None):
    if driver is None:
        driver = create_driver()
    driver.login()
    audits = driver.users.get_user_audits(user_id)
    if VERBOSE:
        pprint(audits)
    return audits
