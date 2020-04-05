'''
afficher toutes les équipes d'un bot appartenant à un serveur
'''
import mattermostdriver
from robert_le_robot import read_token, get_options, create_driver
from pprint import pprint

BOT_USERNAME = 'robert_le_robot'

# BOT_USERNAME = 'mauvais_nom_pour_tester' # debug


def display_teams():
    '''
    affiche dans la console toutes les équipes Mattermost d'un bot
    '''
    driver = create_driver()
    driver.login()
    bot_id = None
    try:
        mattermost_bot_user = driver.users.get_user_by_username(BOT_USERNAME)
        bot_id = mattermost_bot_user.get('id')
    except mattermostdriver.exceptions.ResourceNotFound as e:
        print()
        print(repr(e))
        # raise e # debug
    if bot_id is None:
        print('''
Pas d'utilisateur sous le nom {}
Vous pouvez modifier directement la variable BOT_USERNAME dans ce fichier'''.format(BOT_USERNAME))
        return
    mattermost_teams = driver.teams.get_user_teams(bot_id)
    # pprint(mattermost_teams) # debug
    # exit()
    print('\n{0} figure dans {1} teams.'.format(BOT_USERNAME,
                                                len(mattermost_teams)))
    for index, team in enumerate(mattermost_teams):
        text = '''
Team n° {0}
name         : {1}
display_name : {2}
team_id      : {3}
invite_id    : {4}
'''.format(index, team.get('name'), team.get('display_name'),
           team.get('id'), team.get('invite_id'))
        print(text)
    return mattermost_teams


if __name__ == '__main__':
    display_teams()
