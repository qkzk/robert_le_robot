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
from constants import VERBOSE

from responses import Response
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
from responses import PollResponse
from responses import UnderstoodResponse
from responses import StepResponse


class Reply:
    '''choose the corrrect reaction'''

    def __init__(self, parameters):
        self.__parameters = parameters

        self.__keywords_reactions = self.__keyword_reactions()
        self.__response_class = Response
        self.__response_object = None

    def __keyword_reactions(self):
        return {
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
            'poll': PollResponse,
            'compris': UnderstoodResponse,
            'step': StepResponse,
        }

    def bot_replies(self):
        if VERBOSE:
            print("\n##############################################\n")
            print("bot_replies")

        if self.__parameters["channel_id"] is not None:
            self.__response_object = self.__choose_response()
            self.__response_object.bot_response()

    def __choose_response(self):
        '''choisit la bonne réaction et construit la réponse du bot'''
        if VERBOSE:
            print("\n##############################################\n")
            print("bot_command_options received", self.__parameters["command"])

        command_words = self.__parameters["command"].split(' ')

        keyword = command_words[0].lower()
        self.__response_class = self.__keywords_reactions.get(keyword)

        if self.__response_class is None:
            if VERBOSE:
                print("\n##############################################\n")
                print("command_words", command_words)
            if self.__parameters["latex_syntax"]:
                if VERBOSE:
                    print("\n##############################################\n")
                    print("Latex Syntax received")
                self.__response_class = LatexResponse
            else:
                self.__response_class = CannotdoResponse

        return self.__response_class(self.__parameters)
