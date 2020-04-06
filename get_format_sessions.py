'''
Module qui permet de récupérer et présenter la sessions d'un utilisateur

1. se connecter à la bdd (via le serveur qui l'héberge en ssh) et
    y exécute une commande
2. enregistre la dernière commande dans un fichier csv
3. caste le résultat dans une liste de dictionnaire (pourrait utiliser des classes...)
4. formatte le tableau des sessions
'''

import csv
import os
from datetime import datetime
from pprint import pprint

COMMAND_BASH_SESSION = './assiduite/executer_requete_sessions.sh'
PATH_TABLE_SESSIONS = './assiduite/donnees_sessions_brutes.csv'
COMMAND_SESSIONS = '/bin/sh ' + COMMAND_BASH_SESSION + ' {} > ' + PATH_TABLE_SESSIONS
FORMAT_SESSION_DATE = "le %Y-%m-%d à %H:%M"


def get_data_session(username):
    '''(str) -> None'''
    os.system(COMMAND_SESSIONS.format(username))


def read_csv_file(csv_file=PATH_TABLE_SESSIONS):
    '''[csv_file(str)] -> (list)'''
    list_sessions = []
    with open(csv_file) as csvfile:
        fieldnames = ['createat', 'lastactivityat', 'userid']
        csv_dict_reader = csv.DictReader(csvfile,
                                         fieldnames=fieldnames,
                                         delimiter='|')
        for record in csv_dict_reader:
            session = Session.from_csv_row(record)
            if session is not None:
                list_sessions.append(session)
    return list_sessions


def get_parse_data(username):
    '''username(str) -> (list)'''
    get_data_session(username)
    return read_csv_file()


def format_sessions(username, sessions, nb_sessions=10):
    '''username(str), sessions(list) -> (txt)'''
    sessions.sort(key=lambda x: x.createat(), reverse=True)
    sessions = sessions[:nb_sessions]
    text = ''
    for session in sessions:
        text += session.format_session(username)
    return text


def get_format_sessions(username, nb_sessions=10):
    '''username(str) -> (str)'''
    sessions = get_parse_data(username)
    return format_sessions(username, sessions, nb_sessions=nb_sessions)


class Session:
    def __init__(self, createat, lastactivityat, userid):
        self.__createat = createat
        self.__lastactivityat = lastactivityat
        self.__userid = userid

    def createat(self):
        return self.__createat

    def lastactivityat(self):
        return self.__lastactivityat

    def userid(self):
        return self.__userid

    @classmethod
    def from_csv_row(cls, csv_record):
        '''(dict) -> Session'''
        try:
            createat = datetime.fromtimestamp(
                int(csv_record['createat'].strip()) / 1000)
            lastactivityat = datetime.fromtimestamp(
                int(csv_record['lastactivityat'].strip()) / 1000)
            userid = csv_record['userid']
            return Session(createat, lastactivityat, userid)
        except (ValueError, TypeError) as e:
            print(repr(e))
            print("Impossible de caster la session {}".format(csv_record))
            return

    def format_session(self, username):
        '''(str) -> (str)'''
        return 'Connexion de {} '.format(username) + self.__repr__()

    def __repr__(self):
        text = datetime.strftime(self.createat(), FORMAT_SESSION_DATE)
        text += ' jusque '
        text += datetime.strftime(self.lastactivityat(), FORMAT_SESSION_DATE)
        text += '\n'
        return text

    def __str__(self):
        return self.__repr__()


if __name__ == '__main__':
    print(get_format_sessions('qkzk'))
