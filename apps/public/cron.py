
import os
import sys
import django
from datetime import datetime ,timedelta
from libs.utils.mytime import send_toTimestamp
from django.utils import timezone

pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education.settings")

django.setup()

from apps.public.models import SysParam
from apps.order.models import Order,Tranlist
from apps.user.models import Users
from libs.utils.mytime import islimit_time
from django.db import transaction


#匹配超过多少小时未打款封号处理
def task1():
    print("匹配超过多少小时未打款封号处理start...")
    with transaction.atomic():
        sysparam=SysParam.objects.get()

        order=Order.objects.filter(status=0,trantype=0,umark=0)
        if order.exists():
            for item in order:
                if not islimit_time(item.matchtime,sysparam.amount_term):
                    try:
                        user=Users.objects.get(userid=item.userid,status=9)
                        user.status=2
                        user.blockcount +=1
                        user.save()

                        Tranlist.objects.create(**{
                            'trantype':25,
                            'tranname':'超过%d小时未打款封号处理!'%(sysparam.amount_term),
                            'userid':user.userid,
                            'username':user.username
                        })
                    except Users.DoesNotExist:
                        pass


#7天无打款推荐奖清空
def task2():
    print("7天无打款推荐奖清空处理start...")
    t=timezone.now()
    d7 = send_toTimestamp(t - timedelta(days=7))

    users=Users.objects.filter()

    if users.exists():
        for item in users:

            if item.spread == 0 and item.spreadstop == 0:
                continue
            if Order.objects.filter(userid=item.userid, trantype=0, status=2, confirmtime__gte=d7,
                                    confirmtime__lt=send_toTimestamp(t)).count() == 0:

                with transaction.atomic():
                    Tranlist.objects.create(
                        trantype = 26,
                        tranname = '超过7天未打款清空推荐奖',
                        userid = item.userid,
                        username = item.username,
                        bal = item.spread,
                        amount = item.spread * -1
                    )

                    Tranlist.objects.create(
                        trantype = 27,
                        tranname = '超过7天未打款清空推荐奖(冻结)',
                        userid = item.userid,
                        username = item.username,
                        bal = item.spreadstop,
                        amount = item.spreadstop * -1
                    )
                    item.spread = 0
                    item.spreadstop = 0
                    item.save()
