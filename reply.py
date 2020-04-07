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
from mattermost_api import create_driver
from mattermost_api import get_team_from_channel
from mattermost_api import get_user_by_id
from mattermost_api import get_user
from mattermost_api import get_user_sessions_from_api
from utils import get_standard_answers, read_yaml_file

ASSOCIATIONS_TEAM_CLASSROOM = read_yaml_file(PATH_TEAM_CLASSROOM)
FORMAT_SESSION_DATE = "le %Y-%m-%d à %H:%M"


class Reply:
    def __init__(self,
                 command,
                 latex_syntax=False,
                 sender_user_id=None,
                 channel_id=None,
                 team_id=None):
        self.__command = command
        self.__latex_syntax = latex_syntax
        self.__channel_id = channel_id
        self.__team_id = team_id
        self.__sender_user_id = sender_user_id
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
        print("Reply.__format_answer_session received self.__sender_user_id",
              self.__sender_user_id, type(self.__sender_user_id))
        sender_info = get_user_by_id(self.__sender_user_id)
        is_admin = self.__is_role_admin(sender_info)
        username = self.__get_user_name_from_info(sender_info)

        if is_admin:
            user_asked_about = self.__command.split("session")[1].strip()
            try:
                user_id_asked_about = self.__get_user_id_from_username(
                    user_asked_about)

                sessions = get_user_sessions_from_api(user_id_asked_about)
                # print('\n#############################\n')
                # print("\nsessions_received\n")
                # pprint(sessions)
                # print('\n#############################\n')
                answer = self.__format_session_from_api(sessions,
                                                        user_asked_about)
                if answer == "":
                    answer = self.__standard_answers['invalid_user']
            except Exception as e:
                print('\n#############################\n')
                print("\nException raised while asking sessions\n")
                print(repr(e))
                answer = self.__standard_answers['invalid_user']
        else:
            if VERBOSE:
                print("user {0} - {1} session. Permission denied".format(
                    username,
                    self.__sender_user_id
                ))
            answer = self.__standard_answers['cannot_do']
        return answer

    def __format_session_from_api(self, sessions, username):
        answer = ''
        for session in sessions:
            answer += self.__format_session_text(answer, session, username)
        return answer

    def __format_session_text(self, answer, session, username):
        create_at = datetime.fromtimestamp(session.get('create_at') // 1000)
        last_activity_at = datetime.fromtimestamp(
            session.get('last_activity_at') // 1000)

        answer += 'Connexion de {} '.format(username)
        answer += datetime.strftime(create_at, FORMAT_SESSION_DATE)
        answer += ' jusque '
        answer += datetime.strftime(last_activity_at, FORMAT_SESSION_DATE)
        answer += '\n'
        return answer

    def __get_user_id_from_username(self, username):
        user_data = get_user(username)
        return user_data.get("id")

    def __username_from_user_id(self, user_id):
        user_data = get_user_by_id(user_id)
        return user_data.get("username")

    def __get_user_name_from_info(self, sender_info):
        return sender_info.get('username')

    def __is_role_admin(self, sender_info):
        roles = sender_info.get('roles')
        if roles is not None and 'system_admin' in roles:
            return True
        return False

    def __format_answer_cannot_do(self):
        return self.__standard_answers["cannot_do"]
