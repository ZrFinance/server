

import time
from django.utils import timezone


#当前时间转时间戳
def datetime_toTimestamp():
    return time.mktime(timezone.now().timetuple())