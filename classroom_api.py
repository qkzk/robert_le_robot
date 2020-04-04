# from __future__ import print_function
import pickle
import os.path
from pprint import pprint

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly']


courses_name = ['NSI', 'ISN', 'Aéro 2020', '2nde - 2020', 'Test 2019']


def main():
    """Shows basic usage of the Classroom API.
    Prints the names of the first 10 courses the user has access to.
    """
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

    # Call the Classroom API
    results = service.courses().list(pageSize=1000).execute()
    courses = results.get('courses', [])
    my_courses = {}
    if not courses:
        print('No courses found.')
    else:
        print('Courses:')
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
    pprint(my_courses)


if __name__ == '__main__':
    main()
