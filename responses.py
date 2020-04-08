from pprint import pprint
import pydoc

from datetime import datetime

from sympy.parsing.latex import parse_latex

from classroom_api import retrieve_parse_works
from constants import VERBOSE
from constants import DATETIME_FORMAT
# from constants import PATH_ANSWER_HELP
from constants import PATH_TEAM_CLASSROOM
# from constants import PATH_ANSWER_HELP
from utils import get_standard_answers, read_yaml_file

from mattermost_api import get_user_by_id
from mattermost_api import get_user
from mattermost_api import get_user_sessions_from_api
from mattermost_api import get_team_from_channel
from mattermost_api import get_post_for_channel
from mattermost_api import delete_posts_from_list_id
from mattermost_api import get_all_posts_from_username


ASSOCIATIONS_TEAM_CLASSROOM = read_yaml_file(PATH_TEAM_CLASSROOM)


class Response:
    standard_answers = get_standard_answers()

    def __init__(self, parameters):
        self.parameters = parameters
        self.bot = parameters["bot"]
        self.command = parameters["command"]
        self.sender_user_id = parameters["sender_user_id"]
        self.channel_id = parameters["channel_id"]
        self.team_id = parameters["team_id"]
        self.latex_syntax = parameters["latex_syntax"]

    def answer(self):
        return ''

    def reply(self):
        answer = self.answer()
        self.bot.delete_state_for_user(self.sender_user_id)
        return answer


class CannotdoResponse(Response):
    def __init__(self, parameters):
        super(CannotdoResponse, self).__init__(parameters)

    def answer(self):
        return self.standard_answers["cannot_do"]


class HelpResponse(Response):
    def __init__(self, parameters):
        super(HelpResponse, self).__init__(parameters)

    def answer(self):
        return self.standard_answers["help"]
        # with open(PATH_ANSWER_HELP) as f:
        #     return f.read()


class ClassroomResponse(Response):
    def __init__(self, parameters):
        super(ClassroomResponse, self).__init__(parameters)

    def answer(self):
        if VERBOSE:
            print('command : travail !')

        try:
            last_param = self.command.split(' ')[-1]
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

            print("team_id", self.team_id)

            if self.team_id is None or self.team_id == '':
                self.team_id = get_team_from_channel(self.channel_id)

            course_id = ASSOCIATIONS_TEAM_CLASSROOM.get(self.team_id)
            if course_id is not None:
                answer = retrieve_parse_works(how_many=how_many,
                                              course_id=course_id)
            else:
                answer = self.standard_answers["no_classroom"]
        return answer


class DateResponse(Response):
    def __init__(self, parameters):
        super(DateResponse, self).__init__(parameters)

    def answer(self):
        '''
        retourne l'heure formattée
        '''
        now = datetime.now()
        return now.strftime(DATETIME_FORMAT)


class PythonResponse(Response):
    def __init__(self, parameters):
        super(PythonResponse, self).__init__(parameters)

    def answer(self):
        '''
        retourne l'aide d'un module python formattée
        https://stackoverflow.com/questions/15133537/pydoc-render-doc-adds-characters-how-to-avoid-that
        '''
        help_seeked_on = self.command.split("python")[1].strip()
        if VERBOSE:
            print("help_seeked_on", help_seeked_on)
        try:
            answer = pydoc.render_doc(help_seeked_on,
                                      "Voici l'aide de **%s**",
                                      renderer=pydoc.plaintext)[:16383]
        except ImportError as e:
            answer = f"Il n'y a pas d'aide pour **{help_seeked_on}**"
        return answer


class LatexResponse(Response):
    def __init__(self, parameters):
        super(LatexResponse, self).__init__(parameters)

    def answer(self):
        if not self.latex_syntax:
            latex_command = self.command.split("latex")[1].strip()
        else:
            latex_command = self.command
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

    def __init__(self, parameters):
        super(SessionResponse, self).__init__(parameters)

    def answer(self):
        print("Reply.__format_answer_session received selfsender_user_id",
              self.sender_user_id, type(self.sender_user_id))

        sender_info = get_user_by_id(self.sender_user_id)
        is_admin = self.__is_role_admin(sender_info)
        username = self.__get_user_name_from_info(sender_info)

        if is_admin:
            user_asked_about = self.command.split("session")[1].strip()
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
                    self.sender_user_id
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
    def __init__(self, parameters):
        super(ClearResponse, self).__init__(parameters)

    def answer(self):
        sender_info = get_user_by_id(self.sender_user_id)
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
        channel_post_ids = get_post_for_channel(self.channel_id)
        delete_posts_from_list_id(channel_post_ids)


class DeteleResponse(Response):
    def __init__(self, parameters):
        super(DeteleResponse, self).__init__(parameters)

    def answer(self):
        sender_info = get_user_by_id(self.sender_user_id)
        if self.__is_role_admin(sender_info):
            self.__delete_messages()
        else:
            return self.standard_answers["cannot_do"]

    def __delete_messages(self):

        # print("\ndelete messages")
        # print(self.command)
        # username_mentioned = self.command.split('delete')[1].strip()

        bot_status = self.bot.get_state_for_user(self.sender_user_id)
        username_mentioned = ''
        try:
            username_mentioned = bot_status[1].split('delete')[1].strip()
        except (ValueError, IndexError, AttributeError) as e:
            print(repr(e))
            print(bot_status)

        if username_mentioned != '':
            try:
                posts_from_username = get_all_posts_from_username(
                    username_mentioned)
                delete_posts_from_list_id(posts_from_username)
            except Exception as e:
                if VERBOSE:
                    print("__delete_messages")
                    print(repr(e))

    def __is_role_admin(self, sender_info):
        # TODO duplicate
        roles = sender_info.get('roles')
        if roles is not None and 'system_admin' in roles:
            return True
            return False

    def __get_user_id_from_username(self, username):
        # TODO duplicate
        user_data = get_user(username)
        return user_data.get("id")


class AskConfirmationResponse(Response):
    def __init__(self, parameters):
        super(AskConfirmationResponse, self).__init__(parameters)

    def __is_role_admin(self, sender_info):
        roles = sender_info.get('roles')
        if roles is not None and 'system_admin' in roles:
            return True
            return False

    def answer(self):
        sender_info = get_user_by_id(self.sender_user_id)
        if self.__is_role_admin(sender_info):
            return self.standard_answers['confirmer'].format(self.command)
        return self.standard_answers["cannot_do"]

    def reply(self):
        sender_info = get_user_by_id(self.sender_user_id)
        if self.__is_role_admin(sender_info):
            self.bot.set_state_for_user(
                self.sender_user_id,
                (self.channel_id, self.command))
        return self.answer()


class ExecuteConfirmationResponse(Response):
    reactions = {
        'clear': ClearResponse,
        'delete': DeteleResponse,
    }

    def __init__(self, parameters):
        super(ExecuteConfirmationResponse, self).__init__(parameters)

    def answer(self):
        bot_status = self.bot.get_state_for_user(self.sender_user_id)

        answer = self.standard_answers["cannot_do"]
        if bot_status is not None and len(bot_status) > 1:
            asked_for_channel_id, asked_command = bot_status
            if self.channel_id == asked_for_channel_id:
                # trip parameter
                asked_command = asked_command.split(' ')[0]
                reaction_response_class = self.reactions.get(asked_command)
                if reaction_response_class is not None:
                    answer = reaction_response_class(self.parameters).answer()
        return answer
