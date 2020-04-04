# standard library
import pickle
import os.path
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


def create_service():
    '''
    return a service provider
    '''
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
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
    courseWork = {
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
            {'link': {'url': 'https://qkzk.xyz/content/nsi'}},
            {'link': {'url': 'https://qkzk.xyz/content/isn'}}
        ],
        'workType': 'ASSIGNMENT',
        'state': 'PUBLISHED',
    }

    courseWork = service.courses().courseWork().create(
        courseId=course_id, body=courseWork).execute()
    print('Assignment created with ID {0}'.format(courseWork.get('id')))


if __name__ == '__main__':
    create_work()
