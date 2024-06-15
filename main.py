#!/usr/bin/python3
from datetime import datetime
from googleapiclient.discovery import build
from operator import itemgetter
from termcolor import colored
import pickle
import argparse
import os

# Initialize global variables
service = None
calendars = None

def service_gen(filename):
    """Starts a session with the Calendar API service."""
    if not os.path.exists(filename):
        return None
    with open(filename, 'rb') as token:
        cred = pickle.load(token)
    service = build('calendar', 'v3', credentials=cred)
    return service

def get_calendar(calendar_summary):
    """Gets specific calendar information by summary."""
    global calendars
    if not calendar_summary or not calendars:
        return None
    for calendar in calendars:
        if calendar.get('summary') == calendar_summary:
            return calendar
    return None

def calendar_events(calendar_summary, sort_order):
    """Gets events from a specific calendar, sorted by start date."""
    global service
    cal_id = get_calendar(calendar_summary).get('id')
    if not cal_id:
        return []
    items = service.events().list(calendarId=cal_id, maxResults=2500).execute().get('items', [])
    need_items = ['id', 'start', 'summary', 'description', 'location']
    coll_items = []
    for item in items:
        kv_items = {}
        for need_item in need_items:
            if need_item == 'start':
                start_output = item.get(need_item, {}).get('date') or item.get(need_item, {}).get('dateTime')
                kv_items.update({need_item: start_output})
            else:
                kv_items.update({need_item: item.get(need_item)})
        if kv_items.get('start'):
            coll_items.append(kv_items)
    coll_items = sorted(coll_items, key=itemgetter('start'), reverse=sort_order)
    return coll_items

def event_move(calendar_from, event, calendar_to):
    """Moves an event from one calendar to another."""
    calendar_from_id = get_calendar(calendar_from).get('id')
    calendar_to_id = get_calendar(calendar_to).get('id')
    service.events().move(calendarId=calendar_from_id, eventId=event.get('id'), destination=calendar_to_id).execute()
    return True

def event_move_now(calendar_from, event):
    """Moves an event to 'now' in the specified calendar."""
    calendar_from_id = get_calendar(calendar_from).get('id')
    now_date = {'date': datetime.now().strftime("%Y-%m-%d")}
    event['start'] = now_date
    event['end'] = now_date
    service.events().update(calendarId=calendar_from_id, eventId=event.get('id'), body=event).execute()
    return True

def event_delete(calendar_from, event):
    """Deletes an event from the specified calendar."""
    calendar_from_id = get_calendar(calendar_from).get('id')
    service.events().delete(calendarId=calendar_from_id, eventId=event.get('id')).execute()
    return True

def countdown_calculate(event):
    """Calculates countdown in days to the event's start date."""
    start = event['start']
    if 'T' in start:
        given_date = datetime.strptime(start.split('T')[0],"%Y-%m-%d")
    else:
        given_date = datetime.strptime(start, "%Y-%m-%d")
    current_date = datetime.now()
    diff = given_date - current_date
    return diff.days

def count_calendar_event(calendar_from, sort_order):
    """Counts calendar events and prints active and total counts."""
    events = calendar_events(calendar_from, sort_order)
    counter_till_today = 0
    counter_of_all = len(events)
    for event in events:
        if 'T' in event.get('start'):
            datetime_obj = datetime.strptime(event.get('start').split('T')[0], "%Y-%m-%d")
        else:
            datetime_obj = datetime.strptime(event.get('start'), "%Y-%m-%d")
        time_difference = datetime.now() - datetime_obj
        if time_difference.total_seconds() > 0:
            counter_till_today += 1
    print(f"{counter_till_today}|{counter_of_all}")

def event_move_exec(calendar_from, calendar_to, sort_order):
    """Moves events interactively from one calendar to another."""
    events = calendar_events(calendar_from, sort_order)
    if not events:
        return
    for num, event in enumerate(events, start=1):
        info = {
            'id': event.get('id'),
            'summary': event.get('summary'),
            'description': event.get('description'),
            'total': f"{num}/{len(events)}",
            'countdown': countdown_calculate(event)
        }
        print(''.join([f"{colored(k, 'red')}: {info.get(k)}" + '\n' for k in info]))
        input_key = input("(a)rchive (s)kip (q)uit (n)ow \n> ")
        if input_key == 's':
            pass
        if input_key == 'a':
            event_move(calendar_from, event, calendar_to)
        elif input_key == 'q':
            quit()
        elif input_key == 'n':
            event_move_now(calendar_from, event)
        print("========")

def conversion_date_to_standard(date):
    """Converts date to standard format expected by the API."""
    return f"{date}-04:00"

def calendar_import(calendar_to, summary, date_time, description):
    """Imports an event into the specified calendar."""
    global service
    calendar_id = get_calendar(calendar_to).get('id')
    if not calendar_id:
        return False
    date_time = conversion_date_to_standard(date_time)
    dateTime_helper = {'dateTime': date_time, 'timeZone': 'America/New_York'}
    event = {
        'summary': summary,
        'description': description,
        'start': dateTime_helper,
        'end': dateTime_helper
    }
    service.events().insert(calendarId=calendar_id, body=event).execute()
    return True

def present_time():
    """Returns current time in UNIX timestamp."""
    return int(datetime.timestamp(datetime.now()))

def arg_parse():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description='Calendar quick navigation')
    parser.add_argument('-mf', '--move_from', help='Move events from', required=False)
    parser.add_argument('-mt', '--move_to', help='Move events to', required=False)
    parser.add_argument('-c', '--count', help='Count events in calendar', required=False)
    parser.add_argument('-ca', '--countall', help='Count all events in calendar', required=False)
    parser.add_argument('-i', '--importit', help='Import events', required=False)
    parser.add_argument('-C', '--config', help='Config file', required=True)
    parser.add_argument('-s', '--sort', help='Sort order (A/D)', required=True)
    parser.add_argument('-y', '--yaml_gen', help='yaml gen for importing', required=False)
    args = vars(parser.parse_args())
    return args

if __name__ == "__main__":
    args = arg_parse()
    if yaml_gen := args.get('yaml_gen'):
        print("""
        - name: summary
          desc: description
          calendar: Alarm
          date: '2024-06-12'
          time: '19:57:00'
          """)
        exit()
    if config_file := args.get('config'):
        service = service_gen(filename=config_file)
        calendars = service.calendarList().list().execute().get('items', [])
    if sort := args.get('sort'):
        sort_ = (sort == 'D')  # True for descending, False for ascending
    if move_from := args.get('move_from'):
        if move_to := args.get('move_to'):
            event_move_exec(calendar_from=move_from, calendar_to=move_to, sort_order=sort_)
    if count := args.get('count'):
        count_calendar_event(count, sort_)
    if importitme := args.get('importit'):
        import yaml
        yamls = yaml.safe_load_all(open(importitme, 'r'))
        for ya in list(yamls):
            name = ya[0]["name"]
            calendar_name = ya[0]["calendar"]
            desc = ya[0]["desc"]
            date = ya[0]["date"]
            time = ya[0]["time"]
            calendar_import(calendar_name, name, f"{date}T{time}", desc)
