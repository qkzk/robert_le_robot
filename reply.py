'''
Next step : forcer la réponse à Session à un channel privé

get the DM channel id

func GetDMNameFromIds(userId1, userId2 string) string {
    if userId1 > userId2 {
        return userId2 + "__" + userId1
    } else {
        return userId1 + "__" + userId2
    }
'''
from datetime import timedelta
from pprint import pprint

from constants import VERBOSE

from mattermost_api import create_driver

from responses import DateResponse
from responses import CannotdoResponse
from responses import HelpResponse
from responses import ClassroomResponse
from responses import PythonResponse
from responses import LatexResponse
from responses import SessionResponse
from responses import ClearResponse
from responses import DeteleResponse
from responses import AskConfirmationResponse
from responses import ExecuteConfirmationResponse
from responses import DeletePostResponse
from responses import MuteResponse


class Reply:
    def __init__(self,
                 bot,
                 command,
                 latex_syntax=False,
                 sender_user_id=None,
                 channel_id=None,
                 team_id=None,
                 post_id=None,
                 delete_post=False):

        self.__bot = bot
        self.__command = command
        self.__latex_syntax = latex_syntax
        self.__channel_id = channel_id
        self.__team_id = team_id
        self.__post_id = post_id
        self.__sender_user_id = sender_user_id
        self.__delete_post = delete_post

        self.__driver = None
        self.__reply_parameters = None
        self.__post_options = None

        self.__keywords_reactions = self.__define_reactions()

    def __define_reactions(self):
        reactions = {
            'travail': ClassroomResponse,
            'help': HelpResponse,
            'date': DateResponse,
            'python': PythonResponse,
            'latex': LatexResponse,
            'session': SessionResponse,
            'clear': AskConfirmationResponse,
            'delete': AskConfirmationResponse,
            'demander': AskConfirmationResponse,
            'confirmer': ExecuteConfirmationResponse,
            'delete_this_post': DeletePostResponse,
            'mute': MuteResponse,
        }
        return reactions

    def bot_replies(self):
        if VERBOSE:
            print("\n##############################################\n")
            print("bot_replies")
        if self.__channel_id is not None:
            self.__reply_parameters = self.__create_parameters()
            self.__post_options = self.__create_options()

            if VERBOSE:
                print("\nmsg_options")
                pprint(self.__post_options)
            if self.__post_options.get('message') is not None:
                self.__send_reply()
            else:
                if VERBOSE:
                    print("\nbot_replies : answer is None. Nothing sent.")

    def __create_parameters(self):
        return {
            "bot": self.__bot,
            "command": self.__command,
            "sender_user_id": self.__sender_user_id,
            "channel_id": self.__channel_id,
            "team_id": self.__team_id,
            "latex_syntax": self.__latex_syntax,
            "post_id": self.__post_id,
        }

    def __create_options(self):
        '''choisit la bonne réaction et construit la réponse du bot'''
        if VERBOSE:
            print("\n##############################################\n")
            print("bot_command_options received", self.__command)

        words = self.__command.split(' ')

        keyword = words[0].lower()
        self.__response_class = self.__keywords_reactions.get(keyword)

        if self.__response_class is None:
            if VERBOSE:
                print("\n##############################################\n")
                print("words", words)
            if self.__latex_syntax:
                if VERBOSE:
                    print("\n##############################################\n")
                    print("Latex Syntax received")
                self.__response_class = LatexResponse
            else:
                self.__response_class = CannotdoResponse

        self.__response = self.__response_class(self.__reply_parameters)

        return {
            'channel_id': self.__channel_id,
            'message': self.__response.reply(),
        }

    def __send_reply(self):
        self.__driver = create_driver()
        self.__driver.login()
        if VERBOSE:
            print('\nReply send logged in')
        self.__driver.posts.create_post(self.__post_options)
        self.__driver.logout()
