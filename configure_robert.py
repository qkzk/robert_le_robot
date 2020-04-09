from associate_teams_courses import associate_team_classroom
from mattermost_api import add_bot_to_all_teams
from mattermost_api import add_bot_all_channels
from utils import write_to_file
from logging_system import logger

PATH_TOKEN = './config/token.robert'
PATH_OPTION = './config/server_options.yml'

WELCOME_MESSAGE = '''Bienvenue dans l'assistant de configuration de Robert !

Je vais vous guider pas à pas dans la configuration.

Vous pouvez reprendre cette configuration à tout moment si vous n'êtes pas
satisfait.

Avant de lancer la configuration, rendez-vous sur votre serveur et créez un bot.
Vous pouvez aussi créer vos équipes et vos canaux.
Cela me permettra d'y ajouter immédiatement le bot.

Voici les étapez à suivre :

1. Rendez-vous dans : Menu Principal > Intégration > Comptes de bots.
2. Cliquez sur Ajouter un compte de bot.
3. Définissez le nom du bot (recommandé "robert_le_robot" !)
    Le nom d'utilisateur doit commencer par une lettre et contenir entre 3 et 22
    lettres minuscules ou chiffres ou symboles “.”, “-“, et “_”.
4. Copier le token. Je vais vous le demander dans un instant.
5. Rendez le bot administrateur système. (Rôle : administrateur système)
    C'est indispensable pour les options de modération. Il fonctionnera toujours
    sans cela, mais vous ne pourrez pas lui demander d'effacer de messages ou de
    nettoyer un canal.

Quand c'est fait, appuyez sur entrée pour passer à l'étape suivante.
'''
MESSAGE_PRESS_ENTER_AFTER_BOT = "Appuyez sur ENTREE quand vous avez crée votre bot : (ENTREE)"
MESSAGE_ASK_FOR_TOKEN = "Quel est le token du bot ? : "
MESSAGE_ASK_URL = "Quel est l'adresse du serveur ? \n(ne précédez pas par http ou http, juste le nom de domaine) : ? "
MESSAGE_ASK_PORT = "Quel est le port du serveur ? (https : 443, http : 80) ? : "
MESSAGE_ADD_TEAMS = "Je vais ajouter le bots à toutes les teams"
MESSAGE_ADD_BOT_CHANNELS = "Je vais ajouter le bots à tous les canaux publics"
MESSAGE_ASSOCIATE_CLASSROOM = "La dernière étape est l'association entre vos classrooms et les teams"
MESSAGE_CONNECT_CLASSROOM = "Connectez-vous d'abord à google classroom"
MESSAGE_END = """\nVoilà, la configuration du bot est terminée !
Vous pouvez recommencer à tout moment"""


def configure_robert():
    print_welcome()
    ask_input(MESSAGE_PRESS_ENTER_AFTER_BOT)
    bot_token = ask_token()
    write_token(bot_token)

    options = ask_options()
    write_options(options)

    # arrivé ici

    print(MESSAGE_ADD_TEAMS)
    add_bot_to_all_teams()
    print(MESSAGE_ADD_BOT_CHANNELS)
    add_bot_all_channels()

    print(MESSAGE_ASSOCIATE_CLASSROOM)
    print(MESSAGE_CONNECT_CLASSROOM)
    associate_team_classroom()
    print(MESSAGE_END)
    logger.info("Configuration done")


def ask_input(text):
    return input(text)


def print_welcome():
    print(WELCOME_MESSAGE)


def ask_token():
    return ask_input(MESSAGE_ASK_FOR_TOKEN)


def write_token(token):
    write_to_file(PATH_TOKEN, token)


def ask_options():
    url = ask_input(MESSAGE_ASK_URL)
    port = ask_input(MESSAGE_ASK_PORT)
    text = 'basepath: /api/v4\n'
    text += 'debug: false'
    text += 'port: ' + port + '\n'
    text += 'url: ' + url + '\n'
    return text


def write_options(option):
    write_to_file(PATH_OPTION, option)


if __name__ == '__main__':
    configure_robert()
