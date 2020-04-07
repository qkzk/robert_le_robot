from constants import VERBOSE, START_LATEX
from constants import START_COMMAND, END_LATEX
from pprint import pprint
import json
from reply import Reply


class Post:
    def __init__(self, msg_json_data_post, team_id):
        self.__msg_json_data_post = msg_json_data_post
        self.__team_id = team_id
        self.__deal_answer = False
        self.__latex_syntax = False

    @classmethod
    def from_json(cls, msg_json):
        if 'data' in msg_json and 'post' in msg_json['data']:
            msg_json_data_post = msg_json['data']['post']
            team_id = msg_json['data'].get('team_id')
            if VERBOSE:
                print('classmethod : Post from_json')
                pprint(msg_json_data_post)
            return Post(msg_json_data_post, team_id)

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
            channel_id = message.get("channel_id")
            message_content = message.get('message')
            if VERBOSE:
                print("message_content", message_content)
                print("team_id", self.__team_id)

            if message_content.startswith(START_COMMAND):
                command = message_content.split(START_COMMAND)[1]
                if VERBOSE:
                    print("\ncommande reçue")
                    print(command)
                self.__deal_answer = True

            elif message_content.startswith(START_LATEX):
                command = message_content.split(START_LATEX)[1].strip()
                command = command.split(END_LATEX)[0].strip()
                if VERBOSE:
                    print("commande reçue  ", command)
                    print(command)
                self.__latex_syntax = True
                self.__deal_answer = True

            if self.__deal_answer:
                reply = Reply(command,
                              latex_syntax=self.__latex_syntax,
                              channel_id=channel_id,
                              team_id=self.__team_id)
                reply.bot_replies()
