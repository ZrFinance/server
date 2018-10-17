
from utils.mytime import datetime_toTimestamp,string_toTimestamp
from utils.exceptions import PubErrorCustom
from apps.public.models import Verification
from utils.http_request import send_request
from utils.string_extension import md5pass
from datetime import datetime
from apps.order.models import Order
from apps.public.models import SysParam

def check_verification_code(kwargs):
    verification_code=kwargs.get('verification_code')
    mobile=kwargs.get('mobile')

    v=Verification.objects.filter(mobile=mobile,code=verification_code).order_by('-createtime')
    if v.exists():
        v=v[0]
        if v.validtime<datetime_toTimestamp():
            raise PubErrorCustom("验证码失效！")
    else:
        raise PubErrorCustom("验证码不存在！")

import random
def myrandom(num_,r_):
    sum_ = 0
    ran = random.random()
    for num, r in zip(num_, r_):
        sum_ += r
        if ran < sum_ :break
    return num


def smssend(mobile=None,flag=0,vercode=None):
    if flag==0:
        'http://dx110.ipyy.net/smsJson.aspx'

        if isinstance(mobile,list):
            mobiletmp=''
            for item in mobile:
                mobiletmp='{},'.format(item)
            mobile=mobiletmp[:-1]

        send_request(
            url="http://dx110.ipyy.net/smsJson.aspx",
            method='post',
            data={
                'account': '8MYX00159',
                'password': md5pass('8MYX0015998'),
                'mobile' : mobile,
                'content' : '您现在正在注册众瑞金融账户，您的验证码是{}【众瑞金融】'.format(vercode),
                'action' : 'send',
            }
        )



def after_c(sysparam):

    t=datetime.now().strftime("%Y-%m-%d %H:%S:%M")[11:16]

    s=sysparam.morning.split('-')
    start=s[0]
    end=s[1]

    s1=sysparam.after.split('-')
    start1=s1[0]
    end1=s1[1]

    if not (start <= t <= end  or start1 <= t <= end1):
        raise PubErrorCustom("每天排单时间是%s %s"%(sysparam.morning,sysparam.after))

def pdlimit(sysparam):

    t = datetime.now().strftime("%Y-%m-%d %H:%S:%M")

    start = string_toTimestamp(t[:10] + ' 00:00:00')
    end = string_toTimestamp(t[:10] + ' 12:00:00')
    order=Order.objects.filter(createtime__gte=start,createtime__lt=end,status=0,trantype=0)
    if order.exists():
        sum=0
        for item in order:
            sum += item.amount
        if sum > sysparam.morning_amount:
            raise PubErrorCustom("上午排单已超限额!")

    start = string_toTimestamp(t[:10] + ' 12:00:01')
    end = string_toTimestamp(t[:10] + ' 23:59:59')
    order=Order.objects.filter(createtime__gte=start,createtime__lt=end,status=0,trantype=0)
    if order.exists():
        sum=0
        for item in order:
            sum += item.amount
        if sum > sysparam.after_amount:
            raise PubErrorCustom("下午排单已超限额!")






