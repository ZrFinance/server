import random
import time
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import list_route
from core.decorator.response import Core_connector
from utils.exceptions import PubErrorCustom

from apps.public.models import Verification,Banner,Notice,SysParam,Lucky
from apps.order.models import Order,Tranlist
from apps.user.models import Agent,Users

from apps.order.serializers import TranlistSerializer
from apps.public.serializers import VerificationSerializer,LuckySerializer
from apps.user.serializers import AgentSerializer,UsersSerializer
from apps.public.utils import myrandom,smssend,tjjr

from apps.order.serializers import OrderSerializer2
from libs.utils.mytime import islimit_time

from auth.authentication import Authentication

from apps.public.utils import after_c,pdlimit,daytgbzcount,daysqbzcount

import time
import os
from education.settings import BASE_DIR

date = time.strftime('%Y%m%d')
UPLOAD_FILE_PATH = '%s/media/%s/' % (BASE_DIR, date)
isExists = os.path.exists(UPLOAD_FILE_PATH)
if not isExists:
    os.makedirs(UPLOAD_FILE_PATH)

class PublicAPIView(viewsets.ViewSet):

    def get_authenticators(self):
        if self.action_map.get('post') not in ['get_verification_code']:
            return [auth() for auth in [Authentication]]

    @list_route(methods=['GET'])
    @Core_connector()
    def getbanner(self, request, *args, **kwargs):

        banner=Banner.objects.filter()

        if banner.exists():
            data = []
            for item in banner:
                data.append({
                    'id': item.id,
                    'url':item.url,
                })
            data = {'imgs':data}
        else:
            data={'imgs':None}
        return {"data": data}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True,serializer_class=VerificationSerializer,model_class=Verification)
    def get_verification_code(self,requet,*args,**kwargs):

        serializer = kwargs.pop('serializer')
        isinstance=serializer.save()

        smssend(mobile=isinstance.mobile,flag=0,vercode=isinstance.code)

        data={
            "verification_code" : isinstance.code,
        }

        return {"data":data}


    @list_route(methods=['GET'])
    @Core_connector()
    def getnotice(self, request, *args, **kwargs):

        notice=Notice.objects.filter().order_by('-createtime')

        if notice.exists():
            notice = notice[0]
            data={
                'title': notice.title,
                'content': notice.content,
                'createtime': notice.createtime
            }
        else:
            data=None
        return {"data": data}

    def luckyrandom(self,param):



        a = [0, 1, 5, 3, 7]
        b = [param.bfbwzj/100, param.bfb1000/ 100, param.bfb2000/ 100, param.bfb5000 / 100, param.bfb10000/ 100]
        index = myrandom(a, b)
        return index

    @list_route(methods=['GET'])
    @Core_connector()
    def getluckyindex(self, request, *args, **kwargs):
        user = request.user
        try:
            param=SysParam.objects.get()
            index=self.luckyrandom(param)
            after_c(param)
            pdlimit(param)
        except SysParam.DoesNotExist:
            index=0

        user.lastindex = index
        user.save()
        return {"data": {'index': index}}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def clicklucky(self, request, *args, **kwargs):
        user = request.user
        if user.lastindex==1:
            name='幸运认筹1000'
            amount=1000
            vip=1
        elif user.lastindex==3:
            name='幸运认筹5000'
            amount=5000
            vip=2
        elif user.lastindex == 5:
            name = '幸运认筹2000'
            amount=2000
            vip=1
        elif user.lastindex == 7:
            name = '幸运认筹10000'
            amount=10000
            vip=3
        else:
            name = '未知'
        Lucky.objects.create(userid=user.userid,index=user.lastindex,name=name)
        Order.objects.create(
            trantype=0,
            subtrantype=0,
            amount=amount,
            userid=user.userid,
            username=user.username,
            status=0,
            updtime=time.mktime(timezone.now().timetuple())
        )
        amount1 = amount * 2 /100
        if user.buypower < amount1 :
            raise PubErrorCustom('认筹权余额不足！')
        Tranlist.objects.create(
            trantype=3,
            userid=user.userid,
            username=user.username,
            bal=user.buypower,
            amount=amount1*-1
        )
        user.buypower -= amount1

        Tranlist.objects.create(
            trantype=6,
            userid=user.userid,
            username=user.username,
            bal=user.integral,
            amount=vip
        )
        user.integral += vip

        try:
            param=SysParam.objects.get()
            pdlimit(param)
            if daytgbzcount(user.userid, param):
                raise PubErrorCustom('当天提供帮助次数已超!')
            index=self.luckyrandom(param)
        except SysParam.DoesNotExist:
            raise PubErrorCustom("无参数表数据")
            index=0

        user.lastindex = index
        user.save()
        return {"data": {'index': index}}

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def querylucky(self, request, *args, **kwargs):
        user = request.user
        return {'data':LuckySerializer(Lucky.objects.filter(userid=user.userid).order_by('-createtime'),many=True).data}

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def teamquery(self, request, *args, **kwargs):
        user = request.user

        agent1=Users.objects.raw(
            """
                SELECT t2.userid,t1.id,t2.mobile,t2.createtime,t2.status
                FROM user as t2
                INNER JOIN agent as `t1` ON t1.mobile1 = t2.mobile
                WHERE t1.mobile=%s and t1.level ='1'
            """,[user.mobile]
        )
        agent1=list(agent1)

        agent2=Users.objects.raw(
            """
                SELECT t2.userid,t1.id,t2.mobile,t2.createtime,t2.status
                FROM user as `t2`
                INNER JOIN `agent` as `t1` ON t1.mobile1 = t2.mobile
                WHERE t1.mobile=%s and t1.level ='2'
            """,[user.mobile]
        )
        agent2=list(agent2)

        return {'data':{
            'level1count': len(agent1),
            'level2count': len(agent2),
            'level1': AgentSerializer(agent1,many=True).data,
            'level2': AgentSerializer(agent2,many=True).data,
        }}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def activation(self, request, *args, **kwargs):
        user=request.user

        if user.activation < 1:
            raise PubErrorCustom('激活码不足!')
        user.activation -=1
        user.save()

        mobile=self.request.data.get('mobile')
        try:
            user1=Users.objects.get(mobile=mobile)
        except Users.DoesNotExist:
            raise PubErrorCustom("该用户不存在!")

        if user1.status==0:
            raise PubErrorCustom("已激活")
        elif user1.status == 2:
            raise PubErrorCustom("已禁用，不能激活！")

        user1.status=0
        user1.save()

        Tranlist.objects.create(
            trantype=19,
            userid=user.userid,
            username=user.username,
            userid_to=user1.userid,
            username_to=user1.username,
            bal=user.activation,
            amount=-1
        )

        return None

    @list_route(methods=['GET'])
    @Core_connector()
    def userquery(self, request, *args, **kwargs):
        user = request.user
        return {'data':UsersSerializer(user,many=False).data}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def userupd(self, request, *args, **kwargs):
        if request.user.pay_passwd != request.data.get('pay_passwd') :
            raise PubErrorCustom("二级密码错误！")
        if len(request.user.idcard) > 0:
            raise PubErrorCustom("已修改一次，不能再修改！")
        serializer = UsersSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def pay_passwdupd(self, request, *args, **kwargs):
        if request.user.pay_passwd != request.data.get('pay_passwd') :
            raise PubErrorCustom("二级密码错误！")
        request.user.pay_passwd = request.data.get('new_pay_passwd')
        request.user.save()

        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def passwdupd(self, request, *args, **kwargs):
        if request.user.passwd != request.data.get('passwd'):
            raise PubErrorCustom("登录密码错误！")
        request.user.passwd = request.data.get('new_passwd')
        request.user.save()

        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def buypowerupd(self, request, *args, **kwargs):
        username=request.data.get('username')
        amount=request.data.get('amount')
        pay_passwd=request.data.get('pay_passwd')

        user=request.user

        if user.buypower < int(amount):
            raise PubErrorCustom('余额不足！')

        if user.pay_passwd != pay_passwd:
            raise PubErrorCustom('二级密码错误！')

        try:
            user_to = Users.objects.get(username=username)
        except Users.DoesNotExist:
            raise PubErrorCustom('对方账户不存在！')

        if user_to.mobile not in user.agent:
            raise PubErrorCustom('权限不足,无法转账！')

        user.buypower -= int(amount)
        user_to.buypower += int(amount)


        user.save()
        user_to.save()

        Tranlist.objects.create(
            trantype=1,
            userid=user.userid,
            username=user.username,
            userid_to=user_to.userid,
            username_to=user_to.username,
            bal=user.buypower+int(amount),
            amount=int(amount)*-1
        )
        Tranlist.objects.create(
            trantype=2,
            userid=user_to.userid,
            username=user_to.username,
            userid_to=user.userid,
            username_to=user.username,
            bal=user_to.buypower-int(amount),
            amount=int(amount)
        )

        return None


    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def activationupd(self, request, *args, **kwargs):
        username=request.data.get('username')
        amount=request.data.get('amount')
        pay_passwd=request.data.get('pay_passwd')

        user=request.user

        if user.activation < int(amount):
            raise PubErrorCustom('余额不足！')

        if user.pay_passwd != pay_passwd:
            raise PubErrorCustom('二级密码错误！')

        try:
            user_to = Users.objects.get(username=username)
        except Users.DoesNotExist:
            raise PubErrorCustom('对方账户不存在！')

        if user_to.mobile not in user.agent:
            raise PubErrorCustom('权限不足,无法转账！')

        user.activation -= int(amount)
        user_to.activation += int(amount)


        user.save()
        user_to.save()

        Tranlist.objects.create(
            trantype=4,
            userid=user.userid,
            username=user.username,
            userid_to=user_to.userid,
            username_to=user_to.username,
            bal=user.activation+int(amount),
            amount=int(amount)*-1
        )
        Tranlist.objects.create(
            trantype=5,
            userid=user_to.userid,
            username=user_to.username,
            userid_to=user.userid,
            username_to=user.username,
            bal=user_to.activation-int(amount),
            amount=int(amount)
        )

        return None

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def tranlistbquery(self, request, *args, **kwargs):
        user = request.user
        flag = self.request.query_params.get('flag')

        if str(flag)=='0':
            return {'data':TranlistSerializer(Tranlist.objects.filter(userid=user.userid,trantype__in=[1,2,3]),many=True).data}
        elif str(flag)=='1':
            return {'data': TranlistSerializer(Tranlist.objects.filter(userid=user.userid, trantype__in=[4,5]),many=True).data}
        elif str(flag)=='2':
            return {'data': TranlistSerializer(Tranlist.objects.filter(userid=user.userid, trantype__in=[6]),many=True).data}
        elif str(flag)=='3':
            return {'data': TranlistSerializer(Tranlist.objects.filter(userid=user.userid, trantype__in=[11,13,14,22,23]),many=True).data}


    @list_route(methods=['GET'])
    @Core_connector()
    def orderobjquery(self,request,*args,**kwargs):

        order=Order.objects.raw("""
            select t1.ordercode,t3.username,t3.name,t3.mobile,t3.alipay,t3.wechat,t3.bank,t3.bank_account,t3.referee_name,t1.ordercode,t1.updtime
            from `order` as t1
            inner join user as t2 on t1.userid = t2.userid
            inner join user as t3 on t1.userid_to = t3.userid
            where t1.ordercode=%s
        """,[self.request.query_params.get('ordercode')])
        order=list(order)[0]

        return {'data':OrderSerializer2(order,many=False).data}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def orderobconfirm(self,request,*args,**kwargs):
        ordercode=request.data.get('ordercode')

        try:
            order=Order.objects.get(ordercode=ordercode)
        except Order.DoesNotExist:
            raise PubErrorCustom("订单号不存在！")

        try:
            order1=Order.objects.get(ordercode=order.ordercode_to)
        except Order.DoesNotExist:
            raise PubErrorCustom("订单号不存在！")

        if order.trantype == 0:
            raise PubErrorCustom("只有收款方可确认！")

        try:
            sysparam=SysParam.objects.get()
        except SysParam.DoesNotExist:
            raise PubErrorCustom("无规则")

        if islimit_time(order.updtime,2):
            amountlixi=order.amount * sysparam.interset / 100
        else:
            amountlixi=order.amount * sysparam.interset1 / 100

        try:
            user=Users.objects.get(userid=order.userid)
        except Users.DoesNotExist:
            raise PubErrorCustom("该用户不存在!")

        try:
            user1=Users.objects.get(userid=order1.userid)
        except Users.DoesNotExist:
            raise PubErrorCustom("该用户不存在!")

        #本金
        Tranlist.objects.create(
            trantype=9,
            userid=user1.userid,
            username=user1.username,
            userid_to=order1.userid_to,
            username_to=order1.username_to,
            bal=user1.bonus,
            amount=order1.amount,
            ordercode=order1.ordercode
        )

        user.bonus +=order1.amount
        #利息
        Tranlist.objects.create(
            trantype=10,
            userid=user1.userid,
            username=user1.username,
            userid_to=order1.userid_to,
            username_to=order1.username_to,
            bal=user1.bonus,
            amount=amountlixi,
            ordercode = order1.ordercode
        )
        user1.bonus += amountlixi
        user1.save()



        t = time.mktime(timezone.now().timetuple())
        order.updtime = t
        order.status = 2
        order.save()

        order1.updtime = t
        order1.status = 2
        order1.save()

        tjjr(user1,order.amount,order.ordercode,sysparam)
        return None

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def gqfhquery(self,request,*args,**kwargs):
        user=request.user

        return {'data':TranlistSerializer(Tranlist.objects.filter(userid=user.userid,trantype__in=[7,9,10,12]).order_by('-createtime'),many=True).data}



    @list_route(methods=['GET'])
    @Core_connector()
    def tgbzlimitquery(self,request,*args,**kwargs):
        user=request.user

        sysparam=SysParam.objects.get()

        s=list()
        for (index,item) in enumerate(sysparam.help_amount.split(',')):
            s.append({'key':item,'value':item})

        return {'data':s}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def tgbz(self, request, *args, **kwargs):

        user = request.user

        amount=int(request.data.get('amount'))
        pay_passwd=request.data.get('pay_passwd')

        if user.pay_passwd != pay_passwd:
            raise PubErrorCustom("二级密码错误!")

        if daytgbzcount(user.userid,SysParam.objects.get()):
            raise PubErrorCustom('当天提供帮助次数已超!')

        if amount == 1000:
            vip = 1
        elif amount == 2000:
            vip = 1
        elif amount == 5000:
            vip = 2
        elif amount == 10000:
            vip = 3
        elif amount == 15000:
            vip=4
        elif amount == 20000:
            vip=5
        elif amount == 30000:
            vip=7
        else:
            raise PubErrorCustom("金额有误")

        Order.objects.create(
            trantype=0,
            subtrantype=0,
            amount=amount,
            userid=user.userid,
            username=user.username,
            status=0,
            updtime=time.mktime(timezone.now().timetuple())
        )
        amount1 = amount * 2 /100
        if user.buypower < amount1 :
            raise PubErrorCustom('认筹权余额不足！')
        Tranlist.objects.create(
            trantype=17,
            userid=user.userid,
            username=user.username,
            bal=user.buypower,
            amount=amount1*-1
        )
        user.buypower -= amount1

        Tranlist.objects.create(
            trantype=18,
            userid=user.userid,
            username=user.username,
            bal=user.integral,
            amount=vip
        )
        user.integral += vip

        user.save()
        return None


    @list_route(methods=['GET'])
    @Core_connector()
    def xsrcquery(self, request, *args, **kwargs):
        user=request.user

        if Order.objects.filter(userid=user.userid).count():
            return {'data':{"flag":1}}
        else:
            return {'data': {"flag": 2}}



class PublicFileAPIView(viewsets.ViewSet):

    def get_authenticators(self):
        if self.action_map.get('post') not in ['get_verification_code']:
            return [auth() for auth in [Authentication]]

    @list_route(methods=['POST'])
    @Core_connector()
    def upload(self,request, *args, **kwargs):

        file_path = self.request.data.get('file_path')
        file_name = self.request.data.get('file_name')
        file_md5 = self.request.date.get('file_md5')

        base='%s/media/%s'%(BASE_DIR,file_path[-2:])
        new_file_name = '%s_%s' % (file_md5, file_name)
        new_file_path = ''.join([UPLOAD_FILE_PATH, new_file_name])
        with open(new_file_path, 'a') as new_file:
            with open('%s/%s'%(base,file_path[-1:]), 'rb') as f:
                new_file.write(f.read())

        print(base)
        os.removedirs(base)
        return {'data':{'url':'/nginx_upload/%s/%s'%(date,new_file_name)}}



