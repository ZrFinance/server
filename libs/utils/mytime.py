

import time
from django.utils import timezone
from datetime import datetime,timedelta


#当前时间转时间戳
def datetime_toTimestamp():
    return time.mktime(timezone.now().timetuple())

def send_toTimestamp(t):
    t1=str(t)
    t2=time.strptime(t1[0:19],"%Y-%m-%d %H:%M:%S")
    return time.mktime(t2)

def timestamp_toDatetime(timestamp):
    return datetime.fromtimestamp(timestamp)

def diff_day(start, end=datetime.now()):
    d = (end - start).days
    h = (end-start).seconds / 3600

    return d + round(h / 24.0, 1)

#字符串转化为时间戳
def string_toTimestamp(st):
    return time.mktime(time.strptime(st, "%Y-%m-%d %H:%M:%S"))

def islimit_time(start,end):
    t = timestamp_toDatetime(start) + timedelta(hours=end)
    print(t,datetime.now)
    if datetime.now() <= t:
        return True
    else:
        return False

def add_time(start, end):
    t = timestamp_toDatetime(start) + timedelta(hours=end)
    if t <= datetime.now():
        return '00:00:00'
    a = (t - datetime.now()).seconds
    f = a // 60
    s = a % 60

    h = f // 60
    f = f % 60
    return '%02d:%02d:%02d' % (h, f, s)

