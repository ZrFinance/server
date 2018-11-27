
from django.db.models import Q
from utils.mytime import datetime_toTimestamp
from utils.exceptions import PubErrorCustom

from apps.user.models import Users,Agent


def check_passwd(userid,passwd):
    if not Users.objects.filter(userid=userid,passwd=passwd).exists():
        return False
    return True

def check_pay_passwd(userid,passwd):
    if not Users.objects.filter(userid=userid,pay_passwd=passwd).exists():
        return False
    return True


def check_referee_name(kwargs):
    referee_name = kwargs.get('referee_name')
    try:
        user=Users.objects.get(mobile=referee_name)
    except Users.DoesNotExist:
        raise PubErrorCustom("推荐人不存在！")
    return user

def add_referee_name(kwargs):
    referee_name=kwargs.get('referee_name')
    mobile=kwargs.get('mobile')
    user=check_referee_name(kwargs)
    if not user.agent:
        user.agent = mobile
    else:
        user.agent += ',{}'.format(mobile)
    user.save()

    Agent.objects.create(mobile=user.mobile,mobile1=mobile,level=1)
    try:
        agent=Agent.objects.get(mobile1=user.mobile,level=1)
        Agent.objects.create(mobile=agent.mobile,mobile1=mobile,level=2)
    except Agent.DoesNotExist:
        pass

def get_agent(userid):
    pass




