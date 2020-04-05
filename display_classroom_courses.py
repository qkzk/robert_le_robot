'''affiche toutes les courses d'un serveur classroom'''

from pprint import pprint
from classroom_api import create_service, get_courses

SCOPES = ['https://www.googleapis.com/auth/classroom.courses']
PATH_TOKEN_PICKLE_COURSES = './config/token_courses.pickle'
PATH_CREDENTIALS = './config/credentials.json'


def print_courses():
    '''
    Affiche dans la console toutes les classes qu'un utilisateur de google classroom peut voir.
    '''
    my_courses = get_courses(path_token_pickle=PATH_TOKEN_PICKLE_COURSES, scopes=SCOPES,
                             by_tag_name=False)
    for course in my_courses:
        print('id :', course['id'], ', name :', course['name'])
    return my_courses


if __name__ == '__main__':
    print_courses()
