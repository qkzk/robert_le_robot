from datetime import datetime
from datetime import timedelta
import json
from pprint import pprint

from constants import VERBOSE
from constants import START_COMMAND
from constants import START_LATEX
from constants import END_LATEX

from mattermost_api import get_user_by_id

from utils import read_from_file

from reply import Reply


class Post:
    # __bot_id = read_from_file(PATH_ID_BOT)

    def __init__(self, bot, direct_order, msg_json_data_post, team_id):
        self.__bot = bot
        self.__direct_order = direct_order
        self.__msg_json_data_post = msg_json_data_post
        self.__team_id = team_id
        self.__deal_answer = False
        self.__latex_syntax = False
        self.__sender_user_id = None
        self.__post_id = None
        self.__command = None
        self.__channel_id = None
        self.__delete_post = False

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
            self.__post_id = message.get("id")
            message_content = message.get('message')
            senders_user_id = message.get('user_id')
            self.__sender_user_id = senders_user_id

            if self.__sender_user_id == self.__bot.id():
                if VERBOSE:
                    print("\n###################\n")
                    print("OWN MESSAGE READED, SKIP")
                    return

            self.__bot.logger.info(
                "read a post : user_id {} - team_id {} - content {}".format(
                    self.__sender_user_id, self.__team_id, message_content))
            if VERBOSE:
                print("message_content", message_content)
                print("team_id", self.__team_id)

            if self.__bot.get_mode()["mode"] == "mute":
                bot_mode = self.__bot.get_mode()
                duration = bot_mode.get("duration")
                date = bot_mode.get("date")
                now = datetime.now()
                back_to_normal = False
                try:
                    seconds_spent = (now - date).seconds
                    if now - date > duration:
                        back_to_normal = True
                    if VERBOSE:
                        print("Post : muted since {} seconds".format(seconds_spent))
                except TypeError as e:
                    if VERBOSE:
                        print(repr(e))

                if back_to_normal:
                    self.__bot.set_mode("normal")

                else:
                    self.__delete_post = self.__check_must_be_deleted()

            if self.__delete_post:
                self.__deal_answer = True
                self.__command = "delete_this_post " + self.__post_id
                self.reply()

            else:
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

    def __check_must_be_deleted(self):
        sender_infos = get_user_by_id(self.__sender_user_id)
        muted_channel = self.__bot.get_mode().get('channel_id')
        print("muted_channel: ", muted_channel)
        print("channel_id: ", self.__channel_id)
        print("sender is not admin ? ", 'system_admin' not in sender_infos.get('roles'))
        if self.__channel_id is not None and self.__channel_id == muted_channel\
                and ('system_admin' not in sender_infos.get('roles')):
            return True
        return False

    def reply(self):
        if self.__deal_answer:
            reply = Reply(self.__bot,
                          self.__command,
                          latex_syntax=self.__latex_syntax,
                          sender_user_id=self.__sender_user_id,
                          channel_id=self.__channel_id,
                          team_id=self.__team_id,
                          post_id=self.__post_id,
                          delete_post=self.__delete_post)
            reply.bot_replies()
