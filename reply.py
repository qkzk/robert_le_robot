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

    def bot_replies(self):
        if VERBOSE:
            print("\n##############################################\n")
            print("bot_replies")
        if self.__channel_id is not None:
            self.__msg_options = self.__create_options()

            if VERBOSE:
                print("\nmsg_options")
                pprint(self.__msg_options)
            if self.__msg_options.get('message') is not None:
                self.__send_reply()
            else:
                if VERBOSE:
                    print("\nbot_replies : answer is None. Nothing sent.")

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
            self.__response = ClassroomResponse(self.__command,
                                                self.__team_id,
                                                self.__channel_id)

        elif self.__command in ['help', 'aide']:
            self.__response = HelpResponse()

        elif self.__command in ["heure", "date", "aujourd'hui"]:
            self.__response = DateResponse()

        elif self.__command.startswith("python"):
            self.__response = PythonResponse(self.__command)

        elif self.__command.startswith("latex") or self.__latex_syntax:
            self.__response = LatexResponse(self.__command, self.__latex_syntax)

        elif self.__command.startswith("session"):
            self.__response = SessionResponse(self.__command,
                                              self.__sender_user_id)

        elif self.__command in ['nettoyer', 'clear', 'clean']:
            self.__response = ClearResponse(self.__channel_id,
                                            self.__sender_user_id)

        elif self.__command in ['delete']:
            self.__response = ClearResponse(self.__command,
                                            self.__channel_id,
                                            self.__sender_user_id)

        else:
            self.__response = CannotdoResponse()

        answer = self.__response.answer()

        options = {
            'channel_id': self.__channel_id,
            'message': answer,
        }
        return options
