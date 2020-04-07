'''
1. lire une commnde avec une permission particulière
2. vérifier le rôle de l'user
    * si l'user a pas le bon rôle, pas répondre
    * si l'user a le bon rôle, répondre via DM


get the DM channel id

func GetDMNameFromIds(userId1, userId2 string) string {
	if userId1 > userId2 {
		return userId2 + "__" + userId1
	} else {
		return userId1 + "__" + userId2
	}
'''
import pydoc
from datetime import datetime
from sympy.parsing.latex import parse_latex

from classroom_api import retrieve_parse_works

from mattermost_api import create_driver
# from robert_le_robot import get_team_classroom
from mattermost_api import get_team_from_channel, get_standard_answers
# from mattermost_api import datetime_format_command
# from robert_le_robot import python_format_help, latex_evaluate_command
# from robert_le_robot import get_format_sessions

from constants import PATH_ANSWER_HELP, DATETIME_FORMAT
from constants import VERBOSE, PATH_TEAM_CLASSROOM
from utils import get_standard_answers, read_yaml_file
from get_format_sessions import get_format_sessions
from pprint import pprint


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
        post_obj = Post.from_json(msg_json)
        post_obj.parse()


def datetime_format_command():
    '''
    retourne l'heure formattée
    '''
    now = datetime.now()
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


def get_team_classroom():
    associations = read_yaml_file(PATH_TEAM_CLASSROOM)
    return associations


class Reply:
    def __init__(self,
                 command,
                 driver=None,
                 latex_syntax=False,
                 channel_id=None,
                 team_id=None):
        self.__command = command
        self.__driver = driver
        self.__latex_syntax = latex_syntax
        self.__channel_id = channel_id
        self.__team_id = team_id

        self.__msg_options = None
        self.__standard_answers = get_standard_answers()

    def bot_replies(self):
        if VERBOSE:
            print("\n##############################################\n")
            print("bot_replies")
        if self.__channel_id is not None:
            self.__msg_options = self.__bot_command_options()

            if VERBOSE:
                print("\nmsg_options")
                pprint(self.__msg_options)
            self.__send_reply()

    def __send_reply(self):
        if self.__driver is None:
            print('\nI DONT HAVE A DRIVER\n')
        if VERBOSE:
            print('\nReply send reply create driver')
        self.__driver = create_driver()
        if VERBOSE:
            print('\nReply send reply created a new driver')
        self.__driver.login()
        if VERBOSE:
            print('\nReply send logged in')
        self.__driver.posts.create_post(self.__msg_options)
        self.__driver.logout()

    def __bot_command_options(self):
        '''choisit la bonne réaction et construit la réponse du bot'''
        if VERBOSE:
            print("\n##############################################\n")
            print("bot_command_options received", self.__command)
        if 'travail' in self.__command:
            if VERBOSE:
                print('command : travail !')
            last_param = self.__command.split(' ')[-1]
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

            print("team_id", self.__team_id)

            if self.__team_id is None or self.__team_id == '':
                self.__team_id = get_team_from_channel(self.__channel_id)

            course_id = associations_teams_classroom.get(self.__team_id)
            if course_id is not None:
                answer = retrieve_parse_works(how_many=how_many,
                                              course_id=course_id)
            else:
                answer = self.__standard_answers["no_classroom"]
        elif self.__command in ['help', 'aide']:
            with open(PATH_ANSWER_HELP) as f:
                answer = f.read()

        elif self.__command in ["heure", "date", "aujourd'hui"]:
            answer = datetime_format_command()

        elif self.__command.startswith("python"):
            help_seeked_on = self.__command.split("python")[1].strip()
            answer = python_format_help(help_seeked_on)

        elif self.__command.startswith("latex") or self.__latex_syntax:
            if not self.__latex_syntax:
                latex_command = self.__command.split("latex")[1].strip()
            else:
                latex_command = self.__command
            try:
                answer = latex_evaluate_command(latex_command)
            except Exception as e:
                answer = self.__standard_answers['invalid_latex']

        elif self.__command.startswith("session"):
            user_asked_about = self.__command.split("session")[1].strip()
            try:
                answer = get_format_sessions(user_asked_about)
                if answer == "":
                    answer = self.__standard_answers['invalid_user']
            except Exception as e:
                print(repr(e))
                answer = self.__standard_answers['invalid_user']

        else:
            answer = self.__standard_answers["cannot_do"]

        options = {
            'channel_id': self.__channel_id,
            'message': answer,
        }
        return options
