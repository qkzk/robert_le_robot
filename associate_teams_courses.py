# standard library
from shutil import copy
from pprint import pprint

# community
import yaml

# own
from display_classroom_courses import print_courses
from display_classroom_courses import SCOPES
from display_classroom_courses import PATH_TOKEN_PICKLE_COURSES
from display_classroom_courses import PATH_CREDENTIALS

from display_teams import display_teams

PATH_ASSOCIATION = './config/association.yml'
PATH_TEAM_CLASSROOM = './config/team_classroom.yml'
PATH_BACKUP = './config/team_classroom_backup.yml'


def associate_team_classroom():

    classroom_courses = print_courses()
    mattermost_teams = display_teams()

    clean_file_input = input("Voulez-vous effacer le précédent fichier d'association ? [y/N]")
    if clean_file_input.lower() in 'yes':
        clean_file_association()

    association = {}
    for team in mattermost_teams:
        # on associe une équippe mattermost à une id
        print("\nÉquipe Mattermost {0}:{1} à une classroom".format(
            team['id'], team['name']
        ))
        has_classroom_input = input(
            "Cette équipe a-t-elle une classroom associée ? [y/N] ")
        if has_classroom_input in 'yesYES':
            # l'utilisateur connait l'id, on lui demande
            user_know_id = input(
                "Connaissez-vous l'id de la course associée ? [y/N] "
            )
            if user_know_id in 'yesYES':
                # l'user a une id, on lui demande et on l'enregistre
                classroom_id = input("collez cette id : ")
                association[team['id']] = classroom_id
                write_association(team['id'], association[team['id']])
            else:
                # est ce que l'utilisateur a reconnu certaines classes ?
                tag = input("Tapez quelques lettres du nom sur classroom : ")
                possible_courses = []
                for course in classroom_courses:
                    if tag.lower() in course['name'].lower():
                        possible_courses.append(course)
                if possible_courses != []:
                    print("J'ai trouvé {0} classesroom qui peuvent correspondre".format(
                        len(possible_courses)))
                    print("Voici les classes qui peuvent correspondre :")
                    for index, course in enumerate(possible_courses):
                        print('n°', index, 'id :', course['id'], ', name :', course['name'])
                    possible_index = input(
                        "n° de la classe pour l'équipe {0} ? [N pour passer] ".format(team['id']))
                    if possible_index not in 'Nn':
                        try:
                            numero = int(possible_index)
                            if numero in list(range(len(possible_courses))):
                                association[team['id']] = possible_courses[numero]['id']
                                write_association(team['id'], association[team['id']])
                            else:
                                print("Ce n'est pas le numéro d'une classe.")
                        except ValueError:
                            print("Ce nombre n'est pas valide")
                else:
                    print("Je n'ai trouvé aucune classe contenant ce mot clé {0}".format(tag))
                print("Voici les associations que j'ai pu créer pour l'instant")
                pprint(association)
    print("voici l'ensemble des associations enregistrées :")
    read_association_file()
    input_record = input("Voulez-vous utiliser ce fichier de configuration ? [y/N] ")
    if input_record.lower() in 'yes':
        copy_associations()
        print("Le fichier enregistré sera maintenant utilisé par robert_le_robot")
        print("Votre précédent fichier est conservé en backup")
    return association


def read_association_file():
    with open(PATH_ASSOCIATION) as f:
        content = f.read()
    print(content)


def write_association(team_id, classroom_id):
    '''
    Ecrit une paire team_id: classroom_id dans le fichier d'association
    '''
    # association[team['id']]

    print("enregistrement de l'association", team_id, classroom_id)

    with open(PATH_ASSOCIATION, 'a+') as outfile:
        yaml.dump({team_id: classroom_id}, outfile, default_flow_style=False)


def clean_file_association():
    open(PATH_ASSOCIATION, 'w').close()


def copy_associations():
    copy(PATH_TEAM_CLASSROOM, PATH_BACKUP)
    copy(PATH_ASSOCIATION, PATH_TEAM_CLASSROOM)


if __name__ == '__main__':
    associate_team_classroom()
