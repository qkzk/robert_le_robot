from pprint import pprint
import pydoc

from datetime import datetime

from sympy.parsing.latex import parse_latex

from classroom_api import retrieve_parse_works
from constants import VERBOSE
from constants import DATETIME_FORMAT
from constants import PATH_ANSWER_HELP
from constants import PATH_TEAM_CLASSROOM
from constants import PATH_ANSWER_HELP
from utils import get_standard_answers, read_yaml_file

from mattermost_api import get_user_by_id
from mattermost_api import get_user
from mattermost_api import get_user_sessions_from_api
from mattermost_api import get_post_for_channel
from mattermost_api import delete_posts_from_list_id


ASSOCIATIONS_TEAM_CLASSROOM = read_yaml_file(PATH_TEAM_CLASSROOM)


class Response:
    standard_answers = get_standard_answers()

    def __init__(self):
        pass

    def answer(self):
        return ''


class CannotdoResponse(Response):
    def __init__(self):
        pass

    def answer(self):
        return self.standard_answers["cannot_do"]


class HelpResponse(Response):
    def __init__(self):
        pass

    def answer(self):
        with open(PATH_ANSWER_HELP) as f:
            return f.read()


class ClassroomResponse(Response):
    def __init__(self, command, team_id, channel_id):
        super(Response, self).__init__()
        self.__command = command
        self.__team_id = team_id
        self.__channel_id = channel_id

    def answer(self):
        if VERBOSE:
            print('command : travail !')

        try:
            last_param = self.__command.split(' ')[-1]
            print("last_param")
            print(last_param)
            can_continue = True
        except (ValueError, TypeError) as e:
            print("ClassroomResponse.answer : impossible to read the command")
            print(repr(e))
            answer = None
            can_continue = False
        if can_continue:
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
                answer = self.standard_answers["no_classroom"]
        return answer


class DateResponse(Response):
    def __init__(self):
        super(Response, self).__init__()

    def answer(self):
        '''
        retourne l'heure formattée
        '''
        now = datetime.now()
        return now.strftime(DATETIME_FORMAT)


class PythonResponse(Response):
    def __init__(self, command):
        self.__command = command
        super(Response, self).__init__()

    def answer(self):
        '''
        retourne l'aide d'un module python formattée
        https://stackoverflow.com/questions/15133537/pydoc-render-doc-adds-characters-how-to-avoid-that
        '''
        help_seeked_on = self.__command.split("python")[1].strip()
        if VERBOSE:
            print("help_seeked_on", help_seeked_on)
        try:
            answer = pydoc.render_doc(help_seeked_on,
                                      "Voici l'aide de **%s**",
                                      renderer=pydoc.plaintext)
        except ImportError as e:
            answer = f"Il n'y a pas d'aide pour **{help_seeked_on}**"
        return answer


class LatexResponse(Response):
    def __init__(self, command, latex_syntax):
        self.__command = command
        self.__latex_syntax = latex_syntax
        super(Response, self).__init__()

    def answer(self):
        if not self.__latex_syntax:
            latex_command = self.__command.split("latex")[1].strip()
        else:
            latex_command = self.__command
        try:
            answer = self.__latex_evaluate_command(latex_command)
        except Exception as e:
            answer = self.standard_answers['invalid_latex']
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


class SessionResponse(Response):

    FORMAT_SESSION_DATE = "le %Y-%m-%d à %H:%M"

    def __init__(self, command, sender_user_id):
        self.__command = command
        self.__sender_user_id = sender_user_id
        super(Response, self).__init__()

    def answer(self):
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
                answer = self.__format_session_from_api(sessions,
                                                        user_asked_about)
                if answer == "":
                    answer = self.standard_answers['invalid_user']
            except Exception as e:
                print("\nException raised while asking sessions\n")
                print(repr(e))
                answer = self.standard_answers['invalid_user']
        else:
            if VERBOSE:
                print("user {0} - {1} session. Permission denied".format(
                    username,
                    self.__sender_user_id
                ))
            answer = self.standard_answers['cannot_do']
        return answer

    def __format_session_from_api(self, sessions, username):
        answer = ''
        for session in sessions:
            answer = self.__format_session_text(answer, session, username)
        return answer

    def __format_session_text(self, answer, session, username):
        create_at = datetime.fromtimestamp(session.get('create_at') // 1000)
        last_activity_at = datetime.fromtimestamp(
            session.get('last_activity_at') // 1000)

        answer += 'Connexion de {} '.format(username)
        answer += datetime.strftime(create_at, self.FORMAT_SESSION_DATE)
        answer += ' jusque '
        answer += datetime.strftime(last_activity_at, self.FORMAT_SESSION_DATE)
        answer += '\n'
        return answer

    def __get_user_id_from_username(self, username):
        user_data = get_user(username)
        return user_data.get("id")
    #
    # def __username_from_user_id(self, user_id):
    #     user_data = get_user_by_id(user_id)
    #     return user_data.get("username")

    def __get_user_name_from_info(self, sender_info):
        return sender_info.get('username')

    def __is_role_admin(self, sender_info):
        roles = sender_info.get('roles')
        if roles is not None and 'system_admin' in roles:
            return True
        return False


class ClearResponse(Response):
    def __init__(self, channel_id, sender_user_id):
        self.__channel_id = channel_id
        self.__sender_user_id = sender_user_id
        pass

    def answer(self):
        sender_info = get_user_by_id(self.__sender_user_id)
        if self.__is_role_admin(sender_info):
            self.__clear_channel()
        else:
            return self.standard_answers["cannot_do"]

    def __is_role_admin(self, sender_info):
        roles = sender_info.get('roles')
        if roles is not None and 'system_admin' in roles:
            return True
            return False

    def __clear_channel(self):
        channel_post_ids = get_post_for_channel(self.__channel_id)
        delete_posts_from_list_id(channel_post_ids)
