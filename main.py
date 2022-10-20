from googleapiclient.discovery import build
import pickle
from termcolor import colored

#import datetime
#from google_auth_oauthlib.flow import Flow, InstalledAppFlow
#from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
#from google.auth.transport.requests import Request


def cred_read(filename):
    with open(filename, 'rb') as token:
        cred = pickle.load(token)
    return cred

cred = cred_read('./token.pickle')
service = build('calendar','v3',credentials=cred)
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
    items = service.events().list(calendarId=cal_id['id']).execute().get('items')
    need_items = ['id','summary','start','description']
    coll_items = []
    for item in items:
        kv_items = {}
        for need_item in need_items:
            if need_item == 'start':
                start_output = item.get(need_item)
                start_output.pop('timeZone',None)
                dates = ['dateTime','date']
                for date in dates:
                    if datex := start_output.get(date):
                        kv_items.update({need_item: datex})
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


events = calendar_events('ToDo')
for num, event in enumerate(events):
    event['total'] = f"{num+1}/{len(events)}"

    for k in event:
        if event.get(k):
            print(f"{colored(k,'red')}: {event.get(k)}")

    inputx = input("(a)rchive (d)elete \n> ")
    
    if inputx == 'a':
        moveTo('ToDo',event.get('id'),'Archive')
    if inputx == 'd':
        deleteTo('ToDo',event.get('id'))
    print("========")