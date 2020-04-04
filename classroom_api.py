# standard library
import pickle
import os.path
from datetime import datetime
# from dateutil.parser import parse
from pprint import pprint

# google
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# perso
from classroom_courses import courses_name, my_courses

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly']
# https://www.googleapis.com/auth/classroom.courses
# https://www.googleapis.com/auth/classroom.coursework.me
# https: // www.googleapis.com/auth/classroom.coursework.students

SCOPES = ['https://www.googleapis.com/auth/classroom.coursework.students']  # modifier les travaux

PATH_MODELE = './responses/modele.md'
PATH_TOKEN_PICKLE = './config/token.pickle'
PATH_CREDENTIALS = './config/credentials.json'


def create_service():
    '''
    return a service provider
    '''
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(PATH_TOKEN_PICKLE):
        with open(PATH_TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                PATH_CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(PATH_TOKEN_PICKLE, 'wb') as token:
            pickle.dump(creds, token)

    service = build('classroom', 'v1', credentials=creds)
    return service


def get_courses(service=None):
    """Shows basic usage of the Classroom API.
    return the courses that matches the tag names
    """
    if service is None:
        service = create_service()
    # Call the Classroom API
    results = service.courses().list(pageSize=1000).execute()
    courses = results.get('courses', [])
    my_courses = {}
    if not courses:
        print('No courses found.')
    else:
        # print('Courses:')
        for course in courses:
            name = course['name']
            for tag in courses_name:
                if tag in name:
                    # print('\n', course['name'])
                    # pprint(course['id'])
                    my_courses[tag] = {
                        'tag': tag,
                        'name': course['name'],
                        'id': course['id'],
                        'courseGroupEmail': course['courseGroupEmail'],
                        'enrollmentCode': course['enrollmentCode'],
                        'calendarId': course['calendarId'],
                        'courseGroupEmail': course['courseGroupEmail']
                    }
    return my_courses


def tester_tlm():
    assert my_courses == get_courses()


def create_work():
    service = create_service()
    course_id = my_courses['Test 2019']['id']
    contenu = {
        'title': 'Le titre - from python',
        'description': '''Le contenu de la description
voilà sur plusieurs ligne
un nouveau retour à la ligne

**du gras avec MD ?**

* une liste md ???

# Un titre md ??

<ul>
    <li>une liste html ?</li>
</ul>
        ''',
        'materials': [
            {'link': {'url': 'https://qkzk.xyz/docs/nsi'}},
            {'link': {'url': 'https://qkzk.xyz/docs/isn'}}
        ],
        'workType': 'ASSIGNMENT',
        'state': 'PUBLISHED',
    }

    course_work = service.courses().courseWork().create(
        courseId=course_id, body=contenu).execute()
    print('Assignment created with ID {0}'.format(course_work.get('id')))


def get_work_list(course_id=None):
    service = create_service()
    if course_id is None:
        tag = 'NSI'
        course_id = my_courses[tag]['id']
    work_data = service.courses().courseWork().list(
        courseId=course_id, orderBy='dueDate desc').execute()
    return work_data['courseWork']


def parse_work_list(work_list, how_many=1, course_id=None):
    # print(len(work_list))
    how_many = min(len(work_list), how_many)
    complete_string = ''
    for index, work in enumerate(work_list[:how_many]):
        work_simplified = {
            'title': work.get('title'),  # str
            'url': work.get('alternateLink'),  # str
            'dueDate': work.get('dueDate'),  # {'day': 10, 'month': 4, 'year': 2020},
            'dueTime': work.get('dueTime'),  # {'hours': 21, 'minutes': 59}
            'updateTime': work.get('updateTime'),  # '2020-04-03T11:17:30.322Z'
            'workType': work.get('workType'),  # 'ASSIGNMENT'

        }
        complete_string += 'Travail n° {0} :\n'.format(index + 1)
        complete_string += format_work_mattermost(work_simplified) + '\n\n'
    return complete_string


def get_modele():
    with open(PATH_MODELE) as f:
        content = f.read().strip()
    return content


def format_work_mattermost(work_simplified=None):
    if work_simplified is None:
        work_simplified = {'dueDate': {'day': 10, 'month': 4, 'year': 2020},
                           'dueTime': {'hours': 21, 'minutes': 59},
                           'title': 'Vendredi 3 avril - 14h00 stream sur discord',
                           'updateTime': '2020-04-03T11:17:30.322Z',
                           'url': 'https://classroom.google.com/c/MzcyMjU4ODE2NTJa/a/NzMyNjEwMTQ2MTFa/details',
                           'workType': 'ASSIGNMENT'}

    title = work_simplified.get('title')
    url = work_simplified.get('url')
    updateTime = datetime.strptime(work_simplified.get('updateTime'),
                                   '%Y-%m-%dT%H:%M:%S.%f%z')
    given_date_formatted = updateTime.strftime('%Y-%m-%d')
    due_date = work_simplified.get('dueDate')
    if due_date:
        expected_date_formatted = datetime(year=due_date['year'],
                                           month=due_date['month'],
                                           day=due_date['day'])
        expected_date_formatted = expected_date_formatted.strftime('%Y-%m-%d')
    else:
        expected_date_formatted = ''
    string = get_modele()
    string = string.format(title,
                           given_date_formatted,
                           expected_date_formatted,
                           url,)
    return string


def retrieve_parse_works(how_many=1):
    '''return a description of last classroom works for a given class'''
    work_list = get_work_list(course_id=None)  # OK
    return parse_work_list(work_list, how_many=how_many)


if __name__ == '__main__':
    print(retrieve_parse_works(how_many=2))
