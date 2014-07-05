# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Command-line skeleton application for Calendar API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

'''

import argparse
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools
from datetime import datetime, timedelta

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/906046600976/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
    scope=[
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))


def main(argv):
    # Parse the command-line flags.
    flags = parser.parse_args(argv[1:])

    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to the file.
    storage = file.Storage('sample.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(FLOW, storage, flags)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Calendar API.
    service = discovery.build('calendar', 'v3', http=http)

    try:
        # TODO: need to do the following
        # - look up calendar events in upcoming week
        # - create notes in Evernote for each of those meetings
        # - ^^ make sure aren't creating dups!
        # - ^^ call them '[UNFINISHED] meeting notes yey' initially
        # - put reminders for the day before meeting on all Enotes
        # - put links to the Enote file in the calendar description
        # - write bit in README about how I use it: finish notes then reset
        #    reminder for the day OF the meeting

        # Find user's primary calendar
        calendarlist = service.calendarList().list().execute()
        calendars = calendarlist['items']
        for c in calendars:
            if 'primary' in c.keys():
                primary_cal = c
                break
        primary_cal_id = primary_cal['id']

        # Get all events upcoming in the next week
        # TODO: need to fail gracefully on events without 'dateTime' under 'start'
        now = datetime.now()
        # TODO: need to convert this to primary calendar's default timezone
        right_now = datetime.strftime(now, '%Y-%m-%dT%H:%M:%S')+'-08:00'
        week_from_now = datetime.strftime(now + timedelta(days=+7), '%Y-%m-%dT%H:%M:%S')+'-08:00'
        events_in_next_week = service.events().list(calendarId=primary_cal_id, timeMin=right_now, timeMax=week_from_now,
          singleEvents=True, orderBy='startTime', showDeleted=False).execute()
        events_in_next_week = events_in_next_week['items']

        print 'howdy'
        print len(events_in_next_week)
        print 'ok'

        # Clean events for cancellation ghosts
        for e in events_in_next_week:
            if 'summary' not in e:
                events_in_next_week.remove(e)

        # Expand all recurrence "events" to actual instance events instead
        events_to_remove = []
        events_to_add = []

        for e in events_in_next_week:
            if 'recurrence' in e.keys():
                instances = service.events().instances(calendarId=primary_cal_id, eventId=e['id'], timeMin=right_now, timeMax=week_from_now).execute()
                instances = instances['items']
                events_to_remove.append(e)
                events_to_add.extend(instances)

        [events_in_next_week.remove(e) for e in events_to_remove]

        events_in_next_week.extend(events_to_add)

        # Expanding recurrences can create dups, so let's clear those
        unique_events_ids = []
        for e in events_in_next_week:
            unique_events_ids.append(e['id'])
        unique_events_ids = list(set(unique_events_ids))

        print len(events_in_next_week)
        print events_in_next_week[1]
        print len(unique_events_ids)


    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run'
          'the application to re-authorize')


# For more information on the Calendar API you can visit:
#
#   https://developers.google.com/google-apps/calendar/firstapp
#
# For more information on the Calendar API Python library surface you
# can visit:
#
#   https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/
#
# For information on the Python Client Library visit:
#
#   https://developers.google.com/api-client-library/python/start/get_started
if __name__ == '__main__':
    main(sys.argv)
