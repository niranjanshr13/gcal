from googleapiclient.discovery import build
from datetime import datetime
from termcolor import colored
import pickle, argparse

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
    cal_id = get_calendar(calendar_summary).get('id')
    if not cal_id:
        return
    items = service.events().list(calendarId=cal_id).execute().get('items')
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

def event_move(calendar_from, entry_id, calendar_to):
    calendar_from_id = get_calendar(calendar_from).get('id')
    calendar_to_id = get_calendar(calendar_to).get('id')
    service.events().move(
                    calendarId=calendar_from_id,
                    eventId=entry_id,
                    destination=calendar_to_id).execute()
    return True

def event_delete(calendar_from, entry_id):
    calendar_from_id = get_calendar(calendar_from).get('id')
    service.events().delete(
                    calendarId=calendar_from_id,
                    eventId=entry_id).execute()
    return True

def event_move_exec(calendar_from, calendar_to):
    # func to todo calendar to archive calendar
    events = calendar_events(calendar_from)
    if not events:
        return
    for num, event in enumerate(events):
        id = event.get('id')
        if not id:
            return
        event['total'] = f"{num+1}/{len(events)}" # it is done to create a automate loop
        print(''.join([f"{colored(k, 'red')}: {event.get(k)}" + '\n' for k in event]))
        input_key = input("(a)rchive (d)elete \n> ")

        if input_key == 'a':
            event_move(calendar_from,id,calendar_to)
        if input_key == 'd':
            event_delete(calendar_from,id)
        print("========")

def conversion_date_to_standard(date):
    # if date == "2019-11-011:20am"
    # use this format = '%Y-%m-%d%I:%M%p'
    # btw I am tayloring to my needs not your's so fork this.
    # needs output 2015-05-28T09:00:00-07:00
    # strftime('%Y-%m-%d %H:%M:%S')
    date = datetime.fromtimestamp(int(date)).isoformat() + '-04:00'
    return date

def calendar_import(calendar_to, summary, dateTime, description):
    calendar_id = get_calendar(calendar_to).get('id')
    if not calendar_id:
        return
    dateTime = conversion_date_to_standard(dateTime)
    event = {
        'summary': summary,
        'description': description,
        'start':{'dateTime': dateTime,'timeZone': 'America/New_York'},
        'end':{'dateTime': dateTime,'timeZone': 'America/New_York'}
    }
    service.events().insert(calendarId=calendar_id, body=event).execute()
    return True

def present_time():
    unix = int(datetime.timestamp(datetime.now()))
    return unix 

def countdown(calendar_summary):
    events = calendar_events(calendar_summary)
    if not events:
        return
    for event in events:
        y,m,d  = event.get('start').split('-')
        moment = int(datetime(int(y),int(m),int(d),0,0).timestamp())
        now = present_time()
        remaining_days = f"{round((moment - now) / (60 * 60 * 24),3)} days"
        event.update({'remaining': remaining_days})
        print(''.join([f"{colored(k, 'red')}: {event.get(k)}" + '\n' for k in event]))
        print("===")


parser = argparse.ArgumentParser(description='calendar quick navigation')
parser.add_argument('-c','--countdown', help='Countdown Func.', required=False)

# event_move_exec
parser.add_argument('-mf','--move_from', help='event_move_exec from', required=False)
parser.add_argument('-mt','--move_to', help='event_move_exec to', required=False)

args = vars(parser.parse_args())

if value := args.get('countdown'):
    countdown(value)

if move_from := args.get('move_from'):
    if move_to := args.get('move_to'):
        # example: ./main.py -mf 'calendar from name' and -mt 'calendar to name'
        event_move_exec(calendar_from=move_from, calendar_to=move_to)