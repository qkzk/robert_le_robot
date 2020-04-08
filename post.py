import json
from pprint import pprint

from constants import VERBOSE
from constants import START_COMMAND
from constants import START_LATEX
from constants import END_LATEX
from constants import PATH_ID_BOT

from utils import read_from_file

from reply import Reply


class Post:
    __bot_id = read_from_file(PATH_ID_BOT)

    def __init__(self, bot, direct_order, msg_json_data_post, team_id):
        self.__bot = bot
        self.__direct_order = direct_order
        self.__msg_json_data_post = msg_json_data_post
        self.__team_id = team_id
        self.__deal_answer = False
        self.__latex_syntax = False
        self.__sender_user_id = None
        self.__command = None
        self.__channel_id = None

    @classmethod
    def from_json(cls, bot, msg_json):
        if 'event' in msg_json and msg_json['event'] == 'posted':
            if 'data' in msg_json and 'post' in msg_json['data']:
                msg_json_data_post = msg_json['data']['post']
                team_id = msg_json['data'].get('team_id')

                if VERBOSE:
                    print('classmethod : Post from_json')
                    pprint(msg_json_data_post)
                return Post(bot, None, msg_json_data_post, team_id)

    def parse_post(self):
        '''
        extraie la commande lue par le bot, calcule la réponse et l'envoie
        on ne traite que les posts qui commencent par !robert ou ```latex
        '''
        if VERBOSE:
            print("\n###############################################\n")
            print("parse_post")

        if "message" in self.__msg_json_data_post:
            message = json.loads(self.__msg_json_data_post)
            self.__channel_id = message.get("channel_id")
            message_content = message.get('message')
            senders_user_id = message.get('user_id')
            self.__sender_user_id = senders_user_id

            if self.__sender_user_id == self.__bot_id:
                if VERBOSE:
                    print("\n###################\n")
                    print("OWN MESSAGE READ, SKIP")
                    return

            if VERBOSE:
                print("message_content", message_content)
                print("team_id", self.__team_id)

            if message_content.startswith(START_COMMAND):
                self.__command = message_content.split(START_COMMAND)[1]
                if VERBOSE:
                    print("\ncommande reçue")
                    print(self.__command)
                self.__deal_answer = True

            elif message_content.startswith(START_LATEX):
                self.__command = message_content.split(START_LATEX)[1].strip()
                self.__command = self.__command.split(END_LATEX)[0].strip()
                if VERBOSE:
                    print("commande reçue  ", self.__command)
                    print(self.__command)
                self.__latex_syntax = True
                self.__deal_answer = True
            self.reply()

    def reply(self):
        if self.__deal_answer:
            reply = Reply(self.__bot,
                          self.__command,
                          latex_syntax=self.__latex_syntax,
                          sender_user_id=self.__sender_user_id,
                          channel_id=self.__channel_id,
                          team_id=self.__team_id)
            reply.bot_replies()
