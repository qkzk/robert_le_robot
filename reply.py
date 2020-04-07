'''
NEXT STEP

1. passer aussi de quoi connaître le niveau d'authorisation d'un user
2. refactorer :
    Classe pour formattage standard :
    après avoir reçu le mot clé, les parametres
    Une classe par type de réponse

    * PythonCommand
    * LatexCommand
    * DateCommand
    * SessionCommand
    * HelpCommand
    * InvalidCommand



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
from pprint import pprint
from datetime import datetime

from sympy.parsing.latex import parse_latex

from classroom_api import retrieve_parse_works
from constants import PATH_ANSWER_HELP, DATETIME_FORMAT
from constants import VERBOSE, PATH_TEAM_CLASSROOM
from get_format_sessions import get_format_sessions
from mattermost_api import create_driver
from mattermost_api import get_team_from_channel
from utils import get_standard_answers, read_yaml_file

ASSOCIATIONS_TEAM_CLASSROOM = read_yaml_file(PATH_TEAM_CLASSROOM)


class Reply:
    def __init__(self,
                 command,
                 latex_syntax=False,
                 channel_id=None,
                 team_id=None):
        self.__command = command
        self.__latex_syntax = latex_syntax
        self.__channel_id = channel_id
        self.__team_id = team_id

        self.__driver = None
        self.__msg_options = None
        self.__standard_answers = get_standard_answers()

    def bot_replies(self):
        if VERBOSE:
            print("\n##############################################\n")
            print("bot_replies")
        if self.__channel_id is not None:
            self.__msg_options = self.__create_options()

            if VERBOSE:
                print("\nmsg_options")
                pprint(self.__msg_options)
            self.__send_reply()

    def __send_reply(self):
        self.__driver = create_driver()
        self.__driver.login()
        if VERBOSE:
            print('\nReply send logged in')
        self.__driver.posts.create_post(self.__msg_options)
        self.__driver.logout()

    def __create_options(self):
        '''choisit la bonne réaction et construit la réponse du bot'''
        if VERBOSE:
            print("\n##############################################\n")
            print("bot_command_options received", self.__command)
        if 'travail' in self.__command:
            answer = self.__format_answer_classroom()

        elif self.__command in ['help', 'aide']:
            answer = self.__format_answer_aide()

        elif self.__command in ["heure", "date", "aujourd'hui"]:
            answer = self.__format_answer_date()

        elif self.__command.startswith("python"):
            answer = self.__format_answer_python()

        elif self.__command.startswith("latex") or self.__latex_syntax:
            answer = self.__format_answer_latex()

        elif self.__command.startswith("session"):
            answer = self.__format_answer_session()

        else:
            answer = self.__format_answer_cannot_do()

        options = {
            'channel_id': self.__channel_id,
            'message': answer,
        }
        return options

    def __format_answer_aide(self):
        with open(PATH_ANSWER_HELP) as f:
            return f.read()

    def __format_answer_classroom(self):
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

        print("team_id", self.__team_id)

        if self.__team_id is None or self.__team_id == '':
            self.__team_id = get_team_from_channel(self.__channel_id)

        course_id = ASSOCIATIONS_TEAM_CLASSROOM.get(self.__team_id)
        if course_id is not None:
            answer = retrieve_parse_works(how_many=how_many,
                                          course_id=course_id)
        else:
            answer = self.__standard_answers["no_classroom"]
        return answer

    def __format_answer_date(self):
        '''
        retourne l'heure formattée
        '''
        now = datetime.now()
        return now.strftime(DATETIME_FORMAT)

    def __format_answer_python(self):
        '''
        retourne l'aide d'un module python formattée
        https://stackoverflow.com/questions/15133537/pydoc-render-doc-adds-characters-how-to-avoid-that
        '''
        help_seeked_on = self.__command.split("python")[1].strip()
        # return self.__python_format_help(help_seeked_on)
        if VERBOSE:
            print("help_seeked_on", help_seeked_on)
        try:
            answer = pydoc.render_doc(help_seeked_on,
                                      "Voici l'aide de **%s**",
                                      renderer=pydoc.plaintext)
        except ImportError as e:
            answer = f"Il n'y a pas d'aide pour **{help_seeked_on}**"
        return answer

    def __format_answer_latex(self):
        if not self.__latex_syntax:
            latex_command = self.__command.split("latex")[1].strip()
        else:
            latex_command = self.__command
        try:
            answer = self.__latex_evaluate_command(latex_command)
        except Exception as e:
            answer = self.__standard_answers['invalid_latex']
        return answer

    def __latex_evaluate_command(self, latex_command):
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

    def __format_answer_session(self):
        user_asked_about = self.__command.split("session")[1].strip()
        try:
            answer = get_format_sessions(user_asked_about)
            if answer == "":
                answer = self.__standard_answers['invalid_user']
        except Exception as e:
            print(repr(e))
            answer = self.__standard_answers['invalid_user']
        return answer

    def __format_answer_cannot_do(self):
        return self.__standard_answers["cannot_do"]
