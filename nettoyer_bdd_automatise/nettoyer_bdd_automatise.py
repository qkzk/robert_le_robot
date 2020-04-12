#!/usr/bin/env python3

import glob
import os
import shutil
from datetime import datetime, timezone

PATH_TO_BASH_SQL_COMMANDS = '/home/quentin/nettoyer_bdd_automatise/requete_nettoyer.sh {0}'
PATH_TO_MATTERMOST_FILES_FOLDER = '/home/quentin/mattermost/mattermost-docker/volumes/app/mattermost/data/'
TIMEFORMAT = "%Y%m*"


def a_month_ago():
    '''
    retourne la date du mois dernier
    @return: (datetime)

    source kite :
    https://kite.com/python/answers/how-to-get-a-datetime-representing-one-month-ago-in-python
    '''
    today = datetime.today()

    if today.month == 1:
        one_month_ago = today.replace(year=today.year - 1, month=12)
    else:
        extra_days = 0
        while True:
            try:
                one_month_ago = today.replace(month=today.month - 1,
                                              day=today.day - extra_days)
                break
            except ValueError:
                extra_days += 1
    return one_month_ago


def dt_to_mm_timestamp(dt):
    '''
    retourne une date en timestamp format Mattermost (entier avec les ms )
    @return: (int)

    source tutorialspoint
    https://www.tutorialspoint.com/How-to-convert-Python-date-to-Unix-timestamp

    '''
    return int(dt.replace(tzinfo=timezone.utc).timestamp()) * 1000


def dt_to_fileinfo_folder(dt):
    return dt.strftime(TIMEFORMAT)


def nettoyer(timestamp):
    '''exécute la commande qui va nettoyer la bdd'''
    os.system(PATH_TO_BASH_SQL_COMMANDS.format(timestamp))


def effacer_dossiers(foldername_lastmonth):
    '''
    efface recursivement tous les fichiers du dossier des "files" de Mattermost
    si leur nom contient la chaîne "foldername_lastmonth"
    ce script doit tourner avec sudo

    @param foldername_lastmonth: (str)

    >>> effacer_dossiers("202003")
    # va effacer tous les dossiers de fichiers crées en mars 2020.

    sources :
    1. trouver les bons dossiers (j'ai jamais réussi dans bash directement)
    https://stackoverflow.com/questions/36040884/search-for-a-file-containing-substring-in-a-folder-python
    2. effacer les dossiers en question
    https://stackoverflow.com/questions/13118029/deleting-folders-in-python-recursively
    '''
    pattern = PATH_TO_MATTERMOST_FILES_FOLDER + foldername_lastmonth
    print("pattern :", pattern)
    matching_folders = glob.glob(pattern)
    for matching_folder in matching_folders:

        print("found :", matching_folder)
        try:
            shutil.rmtree(matching_folder)
        except PermissionError as e:
            # si on n'a pas les bons droits
            print(repr(e))
            raise(e)


def piloter():
    '''
    1. calcule le timestamp du mois dernier
    2. exécute la requête correspondante sur la machine distante

            le résultat est que tous les vieux posts sont effacés de la bdd
            mattermost
    3. efface tous les fichiers du mois en question directement sur le dd
    '''
    dt_last_month = a_month_ago()

    timestamp = dt_to_mm_timestamp(dt_last_month)
    nettoyer(timestamp)

    foldername_lastmonth = dt_to_fileinfo_folder(dt_last_month)
    effacer_dossiers(foldername_lastmonth)


if __name__ == '__main__':
    piloter()
