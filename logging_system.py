import logging
import sys

from logging.handlers import RotatingFileHandler

from constants import PATH_LOGFILE
from constants import LOG_FORMAT


def get_module_name():
    return repr(sys.modules[__name__]).split("'")[1].strip()


def setup_app_log(logfile):
    '''
    Crée un logguer avec rotation des fichiers logs
    Enregistre tout dans un seul fichier
    '''
    log_formatter = logging.Formatter(LOG_FORMAT)
    my_handler = RotatingFileHandler(logfile,
                                     mode='a',
                                     maxBytes=5 * 1024 * 1024,
                                     backupCount=2,
                                     encoding=None,
                                     delay=0)
    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(logging.INFO)

    app_log = logging.getLogger(__name__)
    app_log.setLevel(logging.INFO)
    app_log.addHandler(my_handler)

    return app_log


logger = setup_app_log(PATH_LOGFILE)
