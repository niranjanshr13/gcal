from googleapiclient.discovery import build
import pickle
from datetime import datetime

from termcolor import colored

#import datetime
#from google_auth_oauthlib.flow import Flow, InstalledAppFlow
#from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
#from google.auth.transport.requests import Request


def service_gen(filename):
    with open(filename, 'rb') as token:
        cred = pickle.load(token)
    service = build('calendar','v3',credentials=cred)
    return service

service = service_gen(filename='./token.pickle')
calendars = service.calendarList().list().execute().get('items')

def get_calendar(calendar_summary=False):
    if not calendar_summary:
        return
    for calendar in calendars:
        if calendar.get('summary') == calendar_summary:
            return calendar


def calendar_events(calendar_summary):
    cal_id = get_calendar(calendar_summary)
    if not cal_id:
        return
    items = service.events().list(calendarId=cal_id.get('id')).execute().get('items')
    need_items = ['id','start','summary','description','location']
    coll_items = []
    for item in items:
        kv_items = {}
        for need_item in need_items:
            if not item.get(need_item, None):
                continue
            if need_item == 'start':
                if start_output := item.get(need_item):
                    start_output.pop('timeZone', None)
                    datex = list(start_output.values())[0]
                    kv_items.update({need_item: datex })
            else:
                kv_items.update({need_item:item.get(need_item)})
        coll_items.append(kv_items)
    return coll_items

def moveTo(calendar_from, entry_id, calendar_to):
    calendar_from_id = get_calendar(calendar_from).get('id')
    calendar_to_id = get_calendar(calendar_to).get('id')
    service.events().move(
                    calendarId=calendar_from_id,
                    eventId=entry_id,
                    destination=calendar_to_id).execute()
    return True

def deleteTo(calendar_from, entry_id):
    calendar_from_id = get_calendar(calendar_from).get('id')
    service.events().delete(
                    calendarId=calendar_from_id,
                    eventId=entry_id).execute()
    return True

def ToDo_to_Archive(ToDo, Archive):
    # func to todo calendar to archive calendar
    events = calendar_events(ToDo)
    for num, event in enumerate(events):
        event['total'] = f"{num+1}/{len(events)}"
        print(''.join([f"{colored(k, 'red')}: {event.get(k)}" + '\n' for k in event]))
        inputx = input("(a)rchive (d)elete \n> ")

        if inputx == 'a':
            moveTo(ToDo,event.get('id'),Archive)
        if inputx == 'd':
            deleteTo(ToDo,event.get('id'))
        print("========")

#ToDo_to_Archive(ToDo='ToDo', Archive='Archive')

def conversion_date_to_standard(date):
    # if date == "2019-11-011:20am"
    # use this format = '%Y-%m-%d%I:%M%p'
    # btw I am tayloring to my needs not your's so fork this.
    # needs output 2015-05-28T09:00:00-07:00
    # strftime('%Y-%m-%d %H:%M:%S')
    datex = datetime.fromtimestamp(int(date)).isoformat() + '-00:00'
    return datex

def import_from_somewhere(calendar_to, summary, date, description):
    calendar_id = get_calendar(calendar_to)
    # most likely I might prefer to have a event in specific one singular moment than a range.
    event = {
        'summary': summary,
        'description': description,
        'start':{'dateTime': conversion_date_to_standard(date),
                'timeZone': 'America/New_York'},
        'end':{'dateTime': conversion_date_to_standard(date),
            'timeZone': 'America/New_York'
        }
    }
    service.events().insert(calendarId=calendar_id, body=event).execute()
    return True