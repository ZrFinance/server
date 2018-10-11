
from utils.mytime import datetime_toTimestamp
from utils.exceptions import PubErrorCustom
from apps.public.models import Verification,PicVerCode

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

def check_picvercode(kwargs):
    name = kwargs.get('name')
    vercode = kwargs.get('vercode')

    try:
        PicVerCode.objects.get(filename=name,vercode=vercode.lower())
    except PicVerCode.DoesNotExist:
        raise PubErrorCustom("图形验证码输入错误！")


import random
def myrandom(num_,r_):
    sum_ = 0
    ran = random.random()
    for num, r in zip(num_, r_):
        sum_ += r
        if ran < sum_ :break
    return num
