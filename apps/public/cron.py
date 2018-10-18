
import os
import sys
import django

pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education.settings")

django.setup()

from apps.public.models import SysParam
from apps.order.models import Order
from apps.user.models import Users
from libs.utils.mytime import islimit_time
from django.db import transaction


#匹配超过多少小时未打款封号处理
def task1():
    print("匹配超过多少小时未打款封号处理start...")
    with transaction.atomic():
        sysparam=SysParam.objects.get()

        order=Order.objects.filter(status=0,trantype=0)
        if order.exists():
            for item in order:
                if islimit_time(item.updtime,sysparam.amount_term):
                    try:
                        user=Users.objects.get(userid=item.userid,status=9)
                        user.status=2
                        user.blockcount +=1
                        user.save()
                    except Users.DoesNotExist:
                        pass