
from utils.mytime import datetime_toTimestamp,string_toTimestamp
from utils.exceptions import PubErrorCustom
from apps.public.models import Verification

from apps.order.models import Order
from apps.user.models import Agent,Users

from datetime import datetime ,timedelta
from libs.utils.mytime import timestamp_toDatetime,send_toTimestamp

from apps.order.models import Tranlist

from libs.utils.http_request import send_request
from libs.utils.string_extension import md5pass

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

    if isinstance(mobile, list):
        mobiletmp = ''
        for item in mobile:
            mobiletmp = '{},'.format(item)
        mobile = mobiletmp[:-1]
    if flag==0:
        content='您现在正在注册众瑞金融账户，您的验证码是{}【众瑞金融】'.format(vercode)
    elif flag==1:
        content = '【众瑞金融】尊敬的会员您好！您的订单已匹配成功, 请登录查询'
    send_request(
        url="http://dx110.ipyy.net/smsJson.aspx",
        method='post',
        data={
            'account': '8MYX00159',
            'password': md5pass('8MYX0015998'),
            'mobile' : mobile,
            'content' : content,
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
    order=Order.objects.filter(createtime__gte=start,createtime__lt=end,status=0,trantype=0,umark=0)
    if order.exists():
        sum=0
        for item in order:
            sum += item.amount
        if sum > sysparam.morning_amount:
            raise PubErrorCustom("上午排单已超限额!")

    start = string_toTimestamp(t[:10] + ' 12:00:01')
    end = string_toTimestamp(t[:10] + ' 23:59:59')
    order=Order.objects.filter(createtime__gte=start,createtime__lt=end,status=0,trantype=0,umark=0)
    if order.exists():
        sum=0
        for item in order:
            sum += item.amount
        if sum > sysparam.after_amount:
            raise PubErrorCustom("下午排单已超限额!")

def daytgbzcount(userid,sysparam):
    t = datetime.now().strftime("%Y-%m-%d %H:%S:%M")
    start = string_toTimestamp(t[:10] + ' 00:00:01')
    end = string_toTimestamp(t[:10] + ' 23:59:59')
    if Order.objects.filter(userid=userid,createtime__gte=start,createtime__lt=end,trantype=0,umark=0).count() >= sysparam.count1:
        return True
    else:
        return False

def daysqbzcount(userid,sysparam):
    t = datetime.now().strftime("%Y-%m-%d %H:%S:%M")
    start = string_toTimestamp(t[:10] + ' 00:00:01')
    end = string_toTimestamp(t[:10] + ' 23:59:59')
    if Order.objects.filter(userid=userid,createtime__gte=start,createtime__lt=end,trantype=1,umark=0).count() >= sysparam.count2:
        return True
    else:
        return False

def tjjr(user,amount,ordercode,sysparm):

    t=datetime.now()
    d5 = send_toTimestamp(t - timedelta(days=5))
    #代理
    agent_list=[1,2]
    for item in agent_list:
        try:
            agent=Agent.objects.get(mobile1=user.mobile,level=item)
            try:
                user1=Users.objects.get(mobile=agent.mobile)
            except Users.DoesNotExist:
                raise PubErrorCustom("推广奖对应用户不存在!")
            order = Order.objects.filter(userid=user1.userid, trantype=0, status=2, confirmtime__gte=d5,
                                         confirmtime__lt=send_toTimestamp(t),umark=0).order_by('-amount')
            if order.exists():
                order=order[0]
                if amount > order.amount:
                    amount = order.amount
                if item==1:
                    #直推是否有5人间推是否有15人
                    if Agent.objects.filter(mobile=user1.mobile,level=1).count()>=5 and Agent.objects.filter(mobile=user1.mobile,level=2).count()>=15:
                        spread=amount * sysparm.amount9 / 100
                    else:
                        spread=amount * sysparm.amount7 / 100
                elif item==2:
                    #直推是否有5人间推是否有15人
                    if Agent.objects.filter(mobile=user1.mobile,level=1).count()>=5 and Agent.objects.filter(mobile=user1.mobile,level=2).count()>=15:
                        spread=amount * sysparm.amount10 / 100
                    else:
                        spread=amount * sysparm.amount8 / 100

                #推荐奖分两部分(冻结部分待开放)
                # amount2 = spread * sysparm.flag1 / 100
                # amount1 = spread - amount2

                if item == 1:
                    trantype=13
                elif item == 2:
                    trantype=14
                Tranlist.objects.create(
                    trantype=trantype,
                    userid=user1.userid,
                    username=user1.username,
                    bal=user1.spread,
                    amount=spread,
                    ordercode=ordercode
                )

                # if item == 1:
                #     trantype=22
                # elif item == 2:
                #     trantype=23
                # Tranlist.objects.create(
                #     trantype=trantype,
                #     userid=user1.userid,
                #     username=user1.username,
                #     bal=user1.spreadstop,
                #     amount=amount2,
                #     ordercode=ordercode
                # )
                # user1.spreadstop += amount2

                user1.spread += spread
                user1.save()
        except Agent.DoesNotExist:
            pass

def query_agent_limit(mobile,mobile_to):

    if Agent.objects.filter(mobile=mobile,mobile1=mobile_to).count():
        return True

    if Agent.objects.filter(mobile=mobile_to,mobile1=mobile).count():
        return True

    return False

def orderrclimit(user,amount):

    if user.rcqlimit > 0 :
        if amount < user.rcqlimit:
            raise PubErrorCustom("不能低于上次认筹金额%d" % (user.rcqlimit))
    else:
        order=Order.objects.filter(userid=user.userid,umark=0,trantype=0)

        obj=list()
        diffamount=list()
        for item in order:
            obj.append({'ordercode':item.ordercode,'amount':item.amount})
        b = list()
        if len(obj):
            for item in obj:
                if item['ordercode'] in b:
                    continue
                t=list()
                for t_item in Tranlist.objects.filter(trantype=24,ordercode=item['ordercode']):
                    for j in t_item.tranname.split('[')[1].replace(']','')[:-1].split(','):
                        t.append(int(j))
                for j in list(set(t)):
                    if j!=item['ordercode']:
                        try:
                            order = Order.objects.get(ordercode=j, umark=0)
                            item['amount']+=order.amount
                            b.append(j)
                        except Order.DoesNotExist:
                            pass

        for item in obj:
            if item['ordercode'] in b:
                continue
            diffamount.append(item['amount'])

        if len(diffamount):
            maxamount=max(diffamount)
            if amount<maxamount:
                raise PubErrorCustom("不能低于上次认筹金额%d"%(maxamount))


