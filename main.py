import pickle, datetime
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request

cred_pickle = './token.pickle'

with open(cred_pickle, 'rb') as token:
    cred = pickle.load(token)

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
    need_items = ['id','updated','summary','etag','start','created']
    coll_items = []
    for item in items:
        kv_items = {}
        for need_item in need_items:
            kv_items.update({need_item:item.get(need_item)})
        coll_items.append(kv_items)
    return coll_items

def moveTo(calendar_from, entry_etag, calendar_to):
    calendar_from_id = get_calendar(calendar_from).get('id')
    calendar_to_id = get_calendar(calendar_to).get('id')
    service.events().move(
                    calendarId=calendar_from_id,
                    eventId=entry_etag,
                    destination=calendar_to_id).execute()
    return True

events = calendar_events('ToDo')
for event in events:
    print(''.join([f"{k}: {event.get(k)}" + '\n' for k in event]))
    inputx = input("move to archive; type m\n> ")
    if inputx == 'm':
        moveTo('ToDo',event.get('id'),'Archive')
    print("========")