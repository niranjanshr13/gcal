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
echo $(python3 main.py \
        -C $CALENDAR_TOKEN_PICKLE \
        -s A \
        -c ToDo)
```