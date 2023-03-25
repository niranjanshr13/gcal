from datetime import datetime
from googleapiclient.discovery import build
from operator import itemgetter
from termcolor import colored
import pickle, argparse, os


def service_gen(filename):
# a helper func to start the service a session.
    if not os.path.exists(filename):
        return
    with open(filename, 'rb') as token:
        cred = pickle.load(token)
    service = build('calendar','v3',credentials=cred)
    return service


def get_calendar(calendar_summary=False):
# a helper func to get specfic calendar information.
# a global calendar variable should not be touched.
    if not calendar_summary:
        return
    for calendar in calendars:
        if calendar.get('summary') == calendar_summary:
            return calendar


def calendar_events(calendar_summary, sort_):
# a script to get a calendar event by passing a calendar name (calendar_summary)
    cal_id = get_calendar(calendar_summary).get('id')
    if not cal_id:
        return
    items = service.events().list(calendarId=cal_id,  maxResults=2500).execute().get('items')
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
        if kv_items.get('start'):
            coll_items.append(kv_items)
    print(coll_items)
    coll_items = sorted(coll_items, key=itemgetter('start'), reverse=sort_)
    return coll_items

def event_move(calendar_from, entry_id, calendar_to):
# a script to move event from one calendar to another calendar.
# calendar_from: a calendar name; ex: Archive/ToDo
# entry_id: a entry event id
# calendar_to: same as calendar_from but for destination name
# extras: calendar_from|calendar_to needs a calendar name, not calendar id.
    calendar_from_id = get_calendar(calendar_from).get('id')
    calendar_to_id = get_calendar(calendar_to).get('id')
    service.events().move(
                    calendarId=calendar_from_id,
                    eventId=entry_id,
                    destination=calendar_to_id).execute()
    return True

def event_delete(calendar_from, entry_id):
# a script to delete calendar event by passing calendar name and entry id.
    calendar_from_id = get_calendar(calendar_from).get('id')
    service.events().delete(
                    calendarId=calendar_from_id,
                    eventId=entry_id).execute()
    return True

def event_move_exec(calendar_from, calendar_to, sort_):
# interactive func to move entry from one event to another event, with (d)elete feat added.
    events = calendar_events(calendar_from, sort_)
    if not events:
         return
    for num, event in enumerate(events, start=1):
        try:
            id = event.get('id')
            if not id:
                return
            event['total'] = f"{num}/{len(events)}" # it is done to create a automate loop
            print(''.join([f"{colored(k, 'red')}: {event.get(k)}" + '\n' for k in event]))
            input_key = input("(a)rchive (d)elete (q)uit (e)dit_and_(a)rchive \n> ")
            
            if input_key == 'a':
                 event_move(calendar_from,id,calendar_to)
            if input_key == 'd':
                event_delete(calendar_from,id)
            if input_key == 'q':
                exit()
            if input_key == 'ea':
                pass
            print("========")
        except:
            pass

def conversion_date_to_standard(date):
    # if date == "2019-11-011:20am"
    # use this format = '%Y-%m-%d%I:%M%p'
    # btw I am tayloring to my needs not your's so fork this.
    # needs output 2015-05-28T09:00:00-07:00
    # strftime('%Y-%m-%d %H:%M:%S')
    date = datetime.fromtimestamp(int(date)).isoformat() + '-04:00'
    return date

def calendar_import(calendar_to, summary, dateTime, description):
# a helper function to import event by a scripting way.
# probably will not use.
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
# func to get a calendar event and also how many remaining to reach the deadline day.
# ex: a task that needs to done in 10 days, but not now.
# probably will not use, I might stick to my old ways to track that info in another apps.
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


# argparse 
def arg_parse():
    parser = argparse.ArgumentParser(description='calendar quick navigation')
    # countdown
    parser.add_argument('-c','--countdown', help='Countdown Func.', required=False)
    # event_move_exec
    parser.add_argument('-mf','--move_from', help='event_move_exec from', required=False)
    parser.add_argument('-mt','--move_to', help='event_move_exec to', required=False)
    # config
    parser.add_argument('-C','--config', help='config file', required=True)
    parser.add_argument('-s','--sort', help='sort (A/D)', required=True)
    args = vars(parser.parse_args())
    return args

args = arg_parse()

# args matching
if config_file := args.get('config'):
    service = service_gen(filename=config_file) # service var needs to at this place, because of the config args.
    calendars = service.calendarList().list().execute().get('items')

if sort := args.get('sort'):
    if sort == 'A':
        sort_ = False
    if sort == 'D':
        sort_ = True

if value := args.get('countdown'):
    countdown(value)

if move_from := args.get('move_from'):
    if move_to := args.get('move_to'):
# example: ./main.py -mf 'calendar from name' and -mt 'calendar to name'
        event_move_exec(calendar_from=move_from, calendar_to=move_to, sort_=sort_)
