import datetime

def validate(date_text):
    try:
        return datetime.datetime.strptime(date_text, '%Y/%m/%d %H:%M')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY/MM/DD HH:MN")

print(datetime.date.today() - datetime.date(2021, 5, 13))
print(str(datetime.datetime.now()))

print((validate("2021/05/17 10:10") < datetime.datetime(2021, 5, 17, 11, 0, 0)))
print(datetime.datetime(2021, 5, 17, 1, 0, 0) - datetime.timedelta(hours=6))