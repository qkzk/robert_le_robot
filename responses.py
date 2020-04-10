from pprint import pprint
import pydoc

from datetime import datetime
from datetime import timedelta

from sympy.parsing.latex import parse_latex

from classroom_api import retrieve_parse_works

from constants import DATETIME_FORMAT
from constants import DEFAULT_MUTE_DURATION
from constants import PATH_TEAM_CLASSROOM
from constants import VERBOSE

from utils import get_standard_answers, read_yaml_file

from mattermost_api import create_post
from mattermost_api import add_reaction
from mattermost_api import delete_posts_from_list_id
from mattermost_api import delete_this_post
from mattermost_api import get_all_posts_from_username
from mattermost_api import get_user
from mattermost_api import get_user_by_id
from mattermost_api import get_user_id_from_username
from mattermost_api import get_user_sessions_from_api
from mattermost_api import get_post_for_channel
from mattermost_api import get_team_from_channel
from mattermost_api import is_user_admin


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
        self.post_id = parameters["post_id"]

    def answer(self):
        return ''

    def reply(self):
        answer = self.answer()
        self.bot.logger.info("reply sent : {}".format(answer))
        self.bot.delete_state_for_user(self.sender_user_id)
        return answer

    def followup(self, mattermost_answer):
        pass


class CannotdoResponse(Response):
    def __init__(self, parameters):
        super(CannotdoResponse, self).__init__(parameters)

    def answer(self):
        return self.standard_answers["cannot_do"]


class HelpResponse(Response):
    def __init__(self, parameters):
        super(HelpResponse, self).__init__(parameters)

    def answer(self):
        text = self.standard_answers["help"]
        if is_user_admin(self.sender_user_id):
            text += self.standard_answers["help_admin"].format(
                DEFAULT_MUTE_DURATION // 60)
        return text


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
            if VERBOSE:
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
        self.command = self.command.lower()
        help_seeked_on = self.command.split("python")[1].strip()
        if VERBOSE:
            print("help_seeked_on", help_seeked_on)
        try:
            answer = pydoc.render_doc(help_seeked_on,
                                      self.standard_answers['python_doc'],
                                      renderer=pydoc.plaintext)[:16383]
        except ImportError as e:
            answer = self.standard_answers['python_no_doc'].format(help_seeked_on)
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
        sender_info = get_user_by_id(self.sender_user_id)
        is_admin = is_user_admin(self.sender_user_id)

        if is_admin:
            user_asked_about = self.command.split("session")[1].strip()
            try:
                user_id_asked_about = get_user_id_from_username(
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
                print("Permission denied for {0}".format(self.sender_user_id))
            logger.info("Permission denied for {0}".format(self.sender_user_id))
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

        answer += standard_answers['session_start'].format(username)
        answer += datetime.strftime(create_at, self.FORMAT_SESSION_DATE)
        answer += standard_answers['session_end']
        answer += datetime.strftime(last_activity_at, self.FORMAT_SESSION_DATE)
        answer += '\n'
        return answer

    def __get_user_name_from_info(self, sender_info):
        return sender_info.get('username')


class ClearResponse(Response):
    def __init__(self, parameters):
        super(ClearResponse, self).__init__(parameters)

    def answer(self):
        sender_info = get_user_by_id(self.sender_user_id)
        if is_user_admin(self.sender_user_id):
            self.__clear_channel()
        else:
            logger.info("Permission denied for {0}".format(self.sender_user_id))
            return self.standard_answers["cannot_do"]

    def __clear_channel(self):
        channel_post_ids = get_post_for_channel(self.channel_id)
        delete_posts_from_list_id(channel_post_ids)


class DeteleResponse(Response):
    def __init__(self, parameters):
        super(DeteleResponse, self).__init__(parameters)

    def answer(self):
        sender_info = get_user_by_id(self.sender_user_id)
        if is_user_admin(self.sender_user_id):
            self.__delete_messages()
        else:
            logger.info("Permission denied for {0}".format(self.sender_user_id))
            return self.standard_answers["cannot_do"]

    def __delete_messages(self):

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


class AskConfirmationResponse(Response):
    def __init__(self, parameters):
        super(AskConfirmationResponse, self).__init__(parameters)

    def answer(self):
        sender_info = get_user_by_id(self.sender_user_id)
        answer = self.standard_answers["cannot_do"]
        if is_user_admin(self.sender_user_id):
            answer = self.standard_answers['confirmer'].format(self.command)
        self.bot.logger.info("reply sent : {}".format(answer))
        return answer

    def reply(self):
        sender_info = get_user_by_id(self.sender_user_id)
        if is_user_admin(self.sender_user_id):
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


class DeletePostResponse(Response):
    def __init__(self, parameters):
        super(DeletePostResponse, self).__init__(parameters)

    def reply(self):
        sender_info = get_user_by_id(self.sender_user_id)
        post_to_delete = self.command.split("delete_this_post")[1].strip()
        if not is_user_admin(self.sender_user_id):
            if VERBOSE:
                print("\n######## DeletePostResponse : must be deleted")
            delete_this_post(self.post_id)
        return self.answer()

    def answer(self):
        return


class MuteResponse(Response):
    def __init__(self, parameters):
        super(MuteResponse, self).__init__(parameters)
        self.duration = DEFAULT_MUTE_DURATION
        self.stop_mute = False

    def reply(self):
        is_sender_admin = is_user_admin(self.sender_user_id)
        if is_sender_admin:
            try:
                param = self.command.split('mute')[1].strip()
                if param == "off":
                    self.stop_mute = True
                else:
                    self.duration = int(param) * 60
            except (ValueError, IndexError, AttributeError) as e:
                if VERBOSE:
                    print(repr(e))
            if self.stop_mute:
                self.bot.set_channel_mode(self.channel_id, False)
            else:
                self.bot.set_channel_mode(
                    self.channel_id,
                    True,
                    param={"duration": timedelta(seconds=self.duration)})
            return self.answer()

    def answer(self):
        if self.stop_mute:
            return self.standard_answers['mute_off']
        else:
            return self.standard_answers["mute_channel"].format(
                self.duration // 60)


class PollResponse(Response):
    def __init__(self, parameters):
        super(PollResponse, self).__init__(parameters)
        self.poll_question = self.get_poll_options()[0]
        self.poll_options = self.get_poll_options()[2::2]
        self.number_options = len(self.poll_options)
        self.emoji_numbers = {
            0: 'zero',
            1: 'one',
            2: 'two',
            3: 'three',
            4: 'four',
            5: 'five',
            6: 'six',
            7: 'seven',
            8: 'eight',
            9: 'nine',
            10: 'ten',
        }
        self.can_create_poll = True

    def get_poll_options(self):
        question_options = self.command.split('poll')[1]
        if VERBOSE:
            print("\npoll question :")
            pprint(question_options)
        try:
            poll_options = question_options.split('"')[1:]
            if VERBOSE:
                print("\npoll options :")
                pprint(poll_options)
            return poll_options
        except Exception as e:
            print(repr(e))
            return ['']

    def format_answers(self):
        text = self.poll_question
        for index, option in enumerate(self.poll_options):
            text += '\n:' + self.emoji_numbers[index] + ': ' + option
        return text

    def answer(self):
        if self.number_options > 11:
            text = self.standard_answers['too_many_polls']
            self.can_create_poll = False
        else:
            text = self.format_answers()
        return text

    def followup(self, mattermost_answer):

        if VERBOSE:
            print("\n ############### FOLLOWUP ###############\n")
            print(mattermost_answer)
            print("\n ############################## \n")
        if self.can_create_poll:
            post_id = mattermost_answer.get("id")
            bot_id = self.bot.id()
            for index in range(len(self.poll_options)):
                add_reaction(
                    {
                        "user_id": bot_id,
                        "post_id": post_id,
                        "emoji_name": self.emoji_numbers[index],
                        "create_at": 0
                    }
                )
