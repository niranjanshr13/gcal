# gcal
thinking something to do with google calendar, not a big fan of confusing gcalcli

# tutorial
https://karenapp.io/articles/how-to-automate-google-calendar-with-python-using-the-calendar-api/


# examples:
## archiving the event.
```
python3 main.py \
  -C $CALENDAR_TOKEN_PICKLE \
  -mf ToDo \
  -mt Archive \
  -s D
```

## count event (OLD|TOTAL)
```
python3 main.py \
        -C $CALENDAR_TOKEN_PICKLE \
        -s A \
        -c ToDo
```

## importing from yaml file.
```
- name: summary
  desc: description
  calendar: Alarm
  date: '2024-06-12'
  time: '19:57:00'
---
- name: summary
  desc: description
  calendar: Alarm
  date: '2024-06-12'
  time: '19:57:00'

```
