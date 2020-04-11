from datetime import datetime
from datetime import timedelta
import json
from pprint import pprint

from constants import VERBOSE
from constants import START_COMMAND
from constants import START_LATEX
from constants import END_LATEX

from mattermost_api import is_user_admin

from utils import read_from_file

from reply import Reply


class Post:
    def __init__(self, bot, msg_json_data_post, team_id):
        self.__bot = bot
        self.__msg_json_data_post = msg_json_data_post
        self.__team_id = team_id
        self.__deal_answer = False
        self.__latex_syntax = False
        self.__sender_user_id = None
        self.__message_content = None
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
                return Post(bot, msg_json_data_post, team_id)

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
            self.__message_content = message.get('message')
            self.__sender_user_id = message.get('user_id')

            if self.__sender_user_id == self.__bot.id():
                if VERBOSE:
                    print("\n###################\n")
                    print("OWN MESSAGE READED, SKIP")
                    return

            self.__bot.logger.debug(
                "read a post : user_id {} - team_id {} - content {}".format(
                    self.__sender_user_id,
                    self.__team_id,
                    self.__message_content))

            if VERBOSE:
                print("message_content", self.__message_content)
                print("team_id", self.__team_id)

            channel_state = self.__bot.get_channel_mode(self.__channel_id)
            if VERBOSE:
                print("\n##################################")
                print("\n\nPost : channel state\n\n")
                print(channel_state)
                print("mute ???", channel_state.get("mute"))
                print("##################################\n")
            if self.__bot.get_channel_mode(self.__channel_id).get("mute"):
                self.__check_back_normal_or_deleted()

            if self.__delete_post:
                self.__deal_answer = True
                self.__command = "delete_this_post " + self.__post_id
                self.reply()

            else:
                self.__check_command_and_reply()

    def __check_back_normal_or_deleted(self):
        bot_channel_mode = self.__bot.get_channel_mode(self.__channel_id)
        duration = bot_channel_mode.get("duration")
        date_muted = bot_channel_mode.get("date_muted")
        now = datetime.now()
        back_to_normal = False
        if VERBOSE:
            print("\n##################################")
            print("duration", duration)
            print("date_muted", date_muted)
            print("\n##################################")
        try:
            if now - date_muted > duration:
                back_to_normal = True
            if VERBOSE:
                seconds_spent = (now - date_muted).seconds
                print("\n##################################")
                print("\n\nPost : muted since {} seconds\n\n".format(seconds_spent))
                print("##################################\n")
        except TypeError as e:
            if VERBOSE:
                print("\n##################################")
                print("\n\nPost : excetion check back\n\n")
                print(repr(e))
                print("##################################\n")

        if back_to_normal:
            self.__bot.set_channel_mode(self.__channel_id, False)

        else:
            self.__delete_post = self.__check_must_be_deleted()

    def __check_must_be_deleted(self):
        is_muted_channel = self.__bot.get_channel_mode(
            self.__channel_id).get('mute')
        is_sender_admin = is_user_admin(self.__sender_user_id)
        if VERBOSE:
            print("muted_channel ? ", is_muted_channel)
            print("sender is admin ? ", is_sender_admin)
        if is_muted_channel and not is_sender_admin:
            return True

    def __post_to_delete(self, muted_channel, sender_infos):
        return self.__channel_id is not None \
            and self.__channel_id == muted_channel \
            and ('system_admin' not in sender_infos.get('roles'))

    def __check_command_and_reply(self):
        if self.__message_content.startswith(START_COMMAND):
            self.__command = self.__message_content.split(START_COMMAND)[1]
            if VERBOSE:
                print("\ncommande reçue")
                print(self.__command)
            self.__deal_answer = True

        elif self.__message_content.startswith(START_LATEX):
            self.__command = self.__message_content.split(
                START_LATEX)[1].strip()
            self.__command = self.__command.split(END_LATEX)[0].strip()
            if VERBOSE:
                print("commande reçue  ", self.__command)
                print(self.__command)
            self.__latex_syntax = True
            self.__deal_answer = True
        self.reply()

    def __create_parameters(self):
        return {
            "bot": self.__bot,
            "command": self.__command,
            "sender_user_id": self.__sender_user_id,
            "channel_id": self.__channel_id,
            "team_id": self.__team_id,
            "latex_syntax": self.__latex_syntax,
            "post_id": self.__post_id,
            "post_id": self.__post_id,
            "delete_post": self.__delete_post
        }

    def reply(self):
        if self.__deal_answer:
            parameters = self.__create_parameters()
            reply = Reply(parameters)
            reply.bot_replies()
