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


def driver_create(options=None):
    '''
    Retourne une instance de Driver qui permet d'envoyer des commandes
    au serveur
    '''
    if options is None:
        options = get_options()
    driver = Driver(options)
    return driver


def driver_create_login(options=None):
    driver = driver_create(options=None)
    driver.login()
    return driver


def driver_create_login_get_info():
    driver = driver_create()
    result = driver.login()
    bot_id = result.get("id")
    bot_username = result.get("username")
    return driver, bot_id, bot_username


def get_user(username, driver=None):
    '''Retourne les infos d'un utilisateur par son username'''
    if VERBOSE:
        print("\nget user {}".format(username))
    if driver is None:
        driver = driver_create()
    driver.login()
    user = driver.users.get_user_by_username(username)
    if VERBOSE:
        print("\nuser {} is".format(username))
        print(user)
    return user


def get_user_by_id(user_id, driver=None):
    '''Retourne les infos d'un utilisateur par son user_id'''
    assert type(user_id) == str, "get_user_id: user id is not a string"
    if VERBOSE:
        print("\nget user {}".format(user_id))
    if driver is None:
        driver = driver_create()
    driver.login()
    user = driver.users.get_user(user_id)
    if VERBOSE:
        print("\nuser {} is".format(user_id))
        print(user)
    return user


def get_user_id_from_username(username):
    user_data = get_user(username)
    return user_data.get("id")


def is_user_admin(user_id=None, username=None):
    driver = driver_create_login()
    if user_id is None and username is None:
        raise ValueError("You must provide an user_id or a username")
    if user_id is not None:
        user = get_user_by_id(user_id)
    elif username is not None:
        user = get_user(username)
    roles = user.get('roles')
    return roles is not None and "system_admin" in roles


def get_user_sessions_from_api(user_id, driver=None):
    if driver is None:
        driver = driver_create()
    driver.login()
    sessions = driver.users.get_user_sessions(user_id)
    if VERBOSE:
        pprint(sessions)
    return sessions


def get_user_audits_from_api(user_id, driver=None):
    if driver is None:
        driver = driver_create()
    driver.login()
    audits = driver.users.get_user_audits(user_id)
    if VERBOSE:
        pprint(audits)
    return audits


def add_user_to_team(team_id, user_id):
    driver, bot_id, bot_username = driver_create_login_get_info()
    options = {
        "team_id": team_id,
        "user_id": bot_id
    }
    result = driver.teams.add_user_to_team(team_id, options=options)
    driver.logout()
    return result


def get_teams_id():
    driver = driver_create_login()
    teams = driver.teams.get_teams()
    return [team.get('id') for team in teams]


def get_team_from_channel(channel_id, driver=None):
    mattermost_answer = get_channel_info_from_channel_id(channel_id,
                                                         driver=driver)
    team_id = mattermost_answer.get('team_id')
    return team_id


def get_channel_info_from_channel_id(channel_id, driver=None):
    if driver is None:
        driver = driver_create()
    driver.login()
    channel_info = driver.channels.get_channel(channel_id)
    if VERBOSE:
        pprint(channel_info)
    return channel_info


def get_all_channels():
    driver = driver_create_login()
    team_ids = get_teams_id()
    channel_list = []
    for team_id in team_ids:
        channel_list += driver.teams.get_public_channels(team_id)
    return [
        channel.get('id')
        for channel in channel_list
        if channel.get('id') is not None
    ]


def get_post_for_channel(channel_id):
    '''
    methode que j'avais ajouté mais qui n'est pas dans la librairie

    get_posts(self, channel_id):
    return self.client.get(
    self.endpoint + '/' + channel_id + '/posts'
    )

    '''
    driver = driver_create_login()
    # posts = driver.channels.get_posts(channel_id)
    posts = driver.client.get('/channels/' + channel_id + '/posts')

    if VERBOSE:
        print("\n channel post ids :")
        print("\nposts for channel {}".format(channel_id))
        print(posts['order'])
    return posts['order']


def get_ids_from_posts(posts):
    posts_ids = [post['id'] for post in posts]
    if VERBOSE:
        print("\n get ids from posts")
        print("the first ids i got are : ")
        print(posts_ids[:100])
    return posts_ids


def create_post(options, driver=None):
    if driver is None:
        driver = driver_create()
    driver.login()
    mattermost_answer = driver.posts.create_post(options)
    driver.logout()
    return mattermost_answer


def delete_posts_from_list_id(post_ids):
    driver = driver_create_login()
    for post_id in post_ids:
        driver.posts.delete_post(post_id)


def add_reaction(options):
    driver = driver_create_login()
    driver.reactions.create_reaction(options=options)


def add_reaction_list(post_id, bot_id, emojis_list, limit=None):
    if limit is not None:
        emojis_list = emojis_list[:limit]
    for emoji in emojis_list:
        add_reaction(
            {
                "user_id": bot_id,
                "post_id": post_id,
                "emoji_name": emoji,
                "create_at": 0
            }
        )


def delete_this_post(post_id):
    driver = driver_create_login()
    driver.posts.delete_post(post_id)


def get_all_posts_from_username(username):
    '''à editer, il faut encore retrouver les teams_id'''
    teams_id = get_teams_id()
    posts = []
    driver = driver_create_login()
    for team_id in teams_id:
        posts += driver.posts.search_for_team_posts(
            team_id,
            options={'terms': 'from:{}'.format(username)}).get('order')
    return posts


def add_bot_to_list_teams(team_ids):
    driver, bot_id, bot_username = driver_create_login_get_info()
    driver.logout()
    for team_id in team_ids:
        add_user_to_team(team_id, bot_id)


def add_bot_to_all_teams():
    team_ids = get_teams_id()
    add_bot_to_list_teams(team_ids)


def add_bot_all_channels():
    driver, bot_id, bot_username = driver_create_login_get_info()

    channel_ids = get_all_channels()
    for channel_id in channel_ids:
        options = {
            "user_id": bot_id,
        }
        driver.channels.add_user(channel_id, options=options)
