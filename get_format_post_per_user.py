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

COMMAND_BASH_POST_PER_USER = './effacer_user/executer_post_per_user.sh'
PATH_TABLE_POST_PER_USERS = './effacer_user/donnees_post_per_user.csv'
COMMAND_POST_PER_USERS = '/bin/sh ' + COMMAND_BASH_POST_PER_USER + ' {} > ' + PATH_TABLE_POST_PER_USERS


def get_data_post_per_user(username):
    '''(str) -> None'''
    os.system(COMMAND_POST_PER_USERS.format(username))


def read_csv_file(csv_file=PATH_TABLE_POST_PER_USERS):
    '''[csv_file(str)] -> (list)'''
    list_posts = []
    with open(csv_file) as csvfile:
        csv_reader = csv.reader(csvfile,)
        for record in csv_reader:
            list_posts.append(record)
    return list_posts


def get_posts_from_username(username):
    get_data_post_per_user(username)
    return read_csv_file()


if __name__ == '__main__':
    pprint(get_posts_from_username('qkzk'))
