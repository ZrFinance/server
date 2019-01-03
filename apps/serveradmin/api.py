
from rest_framework import viewsets
from rest_framework.decorators import list_route
from core.decorator.response import Core_connector
from utils.exceptions import PubErrorCustom
from apps.serveradmin.models import ServerAdminUser
from apps.order.models import Order,MatchPool,Tranlist
from apps.user.models import Users
from apps.order.serializers import OrderSerializer1
from apps.serveradmin.serializers import MatchPoolSerializer
from apps.user.serializers import UsersSerializer,UsersSerializer1
from apps.serveradmin.serializers import OrderStatusSerializer,TranlistQuerySerializer,SysParamQuerySerializer
import time
from django.utils import timezone
from apps.public.models import SysParam
from libs.utils.mytime import string_toTimestamp
from apps.user.models import Agent,Login,Token

class ServerAdmin(viewsets.ViewSet):

    @list_route(methods=['POST'])
    @Core_connector()
    def login(self, request,*args,**kwargs):

        try:
            user=ServerAdminUser.objects.get(username=request.data.get('username'),passwd=request.data.get('passwd'))
        except ServerAdminUser.DoesNotExist:
            raise PubErrorCustom('登录账号或密码错误！')
        return {'data':{
            'userid':user.userid,
            'username':user.username
        }}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def updpasswd(self,request,*args,**kwargs):
        passwd = request.data.get('passwd',None)
        if not passwd:
            raise PubErrorCustom("密码不能为空!")
        if len(passwd)<6:
            raise PubErrorCustom("密码不能小于6位!")
        ServerAdminUser.objects.filter().update(passwd=passwd)
        return None

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def tgbzquery(self, request,*args,**kwargs):
        flag=self.request.query_params.get('flag',None)
        mobile=self.request.query_params.get('mobile',None)
        amount=self.request.query_params.get('amount',None)
        day = self.request.query_params.get('day', 2)
        ordercode=self.request.query_params.get('ordercode',None)
        value2=self.request.query_params.get('value2',None)

        startdate=self.request.query_params.get('startdate',None)
        enddate=self.request.query_params.get('enddate',None)

        matchauth=self.request.query_params.get('matchauth',None)

        print(self.request.query_params)

        query_params = str()
        query_list = list()

        if mobile:
            query_params = "{} and t2.mobile=%s".format(query_params)
            query_list.append(mobile)
        if amount:
            query_params = "{} and t1.amount=%s".format(query_params)
            query_list.append(amount)
        if ordercode:
            query_params = "{} and t1.ordercode=%s".format(query_params)
            query_list.append(ordercode)
        if value2:
            query_params = "{} and t1.createtime>=%s and t1.createtime<=%s".format(query_params)
            query_list.append(string_toTimestamp(value2[:10] + ' 00:00:01'))
            query_list.append(string_toTimestamp(value2[:10] + ' 23:59:59'))
        if startdate and enddate:
            query_params = "{} and t2.createtime>=%s and t2.createtime<=%s".format(query_params)
            query_list.append(string_toTimestamp(startdate))
            query_list.append(string_toTimestamp(enddate))

        if matchauth:
            query_params = "{} and t2.matchauth=%s".format(query_params)
            query_list.append(matchauth)

        print(query_params)
        print(query_list)

        order=Order.objects.raw(
            """
                SELECT t1.`ordercode`,t2.mobile,t1.amount,t2.name,t1.createtime,t1.status,t2.createtime as registertime
                FROM `order` as t1
                INNER JOIN `user` as t2 ON t1.userid=t2.userid
                WHERE t1.ordercode not in (select ordercode from matchpool) and t1.status=0 and trantype=0 and t1.umark=0 {} ORDER BY createtime desc
            """.format(query_params), query_list)
        order=list(order)

        if flag:
            data=[]
            order1=Order.objects.raw(
                """
                    SELECT t1.ordercode,t1.userid,count(1) as count
                    FROM `order` as t1
                    INNER JOIN `user` as t2 ON t1.userid=t2.userid 
                    WHERE t1.ordercode not in (select ordercode from matchpool) and t1.status=0 and trantype=0 and t1.umark=0 group by t1.userid
                """)
            order1=list(order1)
            if str(flag) == '1':
                for item in order:
                    isflag=False
                    for item1 in order1:
                        if item1.userid==item.userid and item1.count >= 5:
                            isflag=True
                    if isflag:
                        data.append(item)
            elif str(flag) =='2':
                for item in order:
                    isflag=False
                    for item1 in order1:
                        if item1.userid==item.userid and item1.count >= 3 and item1.count < 5 :
                            isflag=True
                    if isflag:
                        data.append(item)
            elif str(flag) == '3':
                for item in order:
                    isflag=False
                    for item1 in order1:
                        if item1.userid==item.userid and item1.count < 3 :
                            isflag=True
                    if isflag:
                        data.append(item)
            else:
                raise PubErrorCustom('isflag错误')

            order=data
        data=OrderSerializer1(order, many=True).data
        data1=list()
        if day!='' and int(day)==1:
            for item in data:
                if item['isday'] >= 5:
                    data1.append(item)
            data=data1
        return {'data':data}

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def jsbzquery(self, request,*args,**kwargs):
        flag=self.request.query_params.get('flag',None)
        mobile=self.request.query_params.get('mobile',None)
        amount=self.request.query_params.get('amount',None)
        day = self.request.query_params.get('day', 2)
        ordercode=self.request.query_params.get('ordercode',None)
        value2=self.request.query_params.get('value2',None)
        startdate=self.request.query_params.get('startdate',None)
        enddate=self.request.query_params.get('enddate',None)

        matchauth=self.request.query_params.get('matchauth',None)

        print(self.request.query_params)

        query_params = str()
        query_list = list()

        if mobile:
            query_params = "{} and t2.mobile=%s".format(query_params)
            query_list.append(mobile)
        if amount:
            query_params = "{} and t1.amount=%s".format(query_params)
            query_list.append(amount)
        if ordercode:
            query_params = "{} and t1.ordercode=%s".format(query_params)
            query_list.append(ordercode)
        if value2:
            query_params = "{} and t1.createtime>=%s and t1.createtime<=%s".format(query_params)
            query_list.append(string_toTimestamp(value2[:10]+' 00:00:01'))
            query_list.append(string_toTimestamp(value2[:10] + ' 23:59:59'))
        if startdate and enddate:
            query_params = "{} and t2.createtime>=%s and t2.createtime<=%s".format(query_params)
            query_list.append(string_toTimestamp(startdate))
            query_list.append(string_toTimestamp(enddate))

        if matchauth:
            query_params = "{} and t2.matchauth=%s".format(query_params)
            query_list.append(matchauth)

        print(query_params)
        print(query_list)
        order=Order.objects.raw(
            """
                SELECT t1.`ordercode`,t2.mobile,t1.amount,t2.name,t1.createtime,t1.status,t2.createtime as registertime
                FROM `order` as t1
                INNER JOIN `user` as t2 ON t1.userid=t2.userid 
                WHERE t1.ordercode not in (select ordercode from matchpool) and t1.status=0 and trantype=1 and t1.umark=0 {} ORDER BY createtime desc
            """.format(query_params), query_list)
        order=list(order)

        if flag:
            data=[]
            order1=Order.objects.raw(
                """
                    SELECT t1.ordercode,t1.userid,count(1) as count
                    FROM `order` as t1
                    INNER JOIN `user` as t2 ON t1.userid=t2.userid 
                    WHERE t1.ordercode not in (select ordercode from matchpool) and t1.status=0 and trantype=1 and t1.umark=0 group by t1.userid
                """)
            order1=list(order1)
            if str(flag) == '1':
                for item in order:
                    isflag=False
                    for item1 in order1:
                        if item1.userid==item.userid and item1.count >= 5:
                            isflag=True
                    if isflag:
                        data.append(item)
            elif str(flag) =='2':
                for item in order:
                    isflag=False
                    for item1 in order1:
                        if item1.userid==item.userid and item1.count >= 3 and item1.count < 5 :
                            isflag=True
                    if isflag:
                        data.append(item)
            elif str(flag) == '3':
                for item in order:
                    isflag=False
                    for item1 in order1:
                        if item1.userid==item.userid and item1.count < 3 :
                            isflag=True
                    if isflag:
                        data.append(item)
            else:
                raise PubErrorCustom('isflag错误')

            order=data
        data=OrderSerializer1(order, many=True).data
        data1=list()
        if day != '' and int(day) == 1:
            for item in data:
                if item['isday'] >= 6:
                    data1.append(item)
            data=data1
        return {'data':data}


    @list_route(methods=['GET'])
    @Core_connector()
    def sysparamquery(self,request,*args,**kwargs):
        return {'data':SysParamQuerySerializer(SysParam.objects.get(),many=False).data}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def sysparamupd(self,request,*args,**kwargs):
        try:
            sysparam=SysParam.objects.get()
        except SysParam.DoesNotExist:
            raise PubErrorCustom('参数不存在')
        morning=request.data.get('morning1')+'-'+request.data.get('morning2')
        after = request.data.get('after1') + '-'+request.data.get('after2')

        request.data['morning']=morning
        request.data['after'] = after
        print(request.data)
        serializer = SysParamQuerySerializer(sysparam, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return None

    @list_route(methods=['GET'])
    @Core_connector()
    def tranlisttrannamequery(self,request,*args,**kwargs):

        data=[
        {
            'trantype':1,
            'tranname':'认筹权转出'
        },
        {
            'trantype':2,
            'tranname':'认筹权转入'
        },
        {
            'trantype':3,
            'tranname':'幸运认筹消耗'
        },
        {
            'trantype':4,
            'tranname':'激活码转出'
        },
        {
            'trantype':5,
            'tranname':'激活码转入'
        },
        {
            'trantype':6,
            'tranname':'转盘投资赠送VIP分'
        },
        {
            'trantype':7,
            'tranname':'系统赠送股权分红'
        },
        {
            'trantype':8,
            'tranname':'系统赠送推广股权'
        },
        {
            'trantype':9,
            'tranname':'投资本金'
        },
        {
            'trantype':10,
            'tranname':'投资利息'
        },
        {
            'trantype':11,
            'tranname':'提取收益扣款(推广股权)'
        },
        {
            'trantype':12,
            'tranname':'提取收益扣款(股份分红)'
        },
        {
            'trantype':13,
            'tranname':'一代奖金'
        },
        {
            'trantype':14,
            'tranname':'二代奖金'
        },
        {
            'trantype':15,
            'tranname':'系统赠送激活码'
        },
        {
            'trantype':16,
            'tranname':'系统赠送认筹权'
        },
        {
            'trantype':17,
            'tranname':'提供帮助认筹消耗'
        },
        {
            'trantype':18,
            'tranname':'提供帮助赠送VIP分'
        },
        {
            'trantype':19,
            'tranname':'激活码激活用户'
        },
        {
            'trantype':20,
            'tranname':'规定时间内无匹配, 推荐奖作废'
        },
        {
            'trantype':21,
            'tranname':'规定时间内无匹配, 推荐奖作废(冻结)'
        },
        {
            'trantype':24,
            'tranname':' 订单拆分'
        },
        {
            'trantype':25,
            'tranname':' 超过指定时间打款封号'
        },
        {
            'trantype':26,
            'tranname':' 超过7天未打款清空推荐奖'
        },
        {
            'trantype':27,
            'tranname':' 超过7天未打款清空推荐奖(冻结)'
        },
        {
            'trantype': 28,
            'tranname': '系统赠送VIP分'
        }]
        return {'data': data}

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def tranlistquery(self, request,*args,**kwargs):
        mobile = self.request.query_params.get('mobile', None)
        trantype = self.request.query_params.get('trantype', None)
        ordercode=self.request.query_params.get('ordercode',None)

        query_params = str()
        query_list = list()

        if mobile:
            query_params = "{} and t2.mobile=%s".format(query_params)
            query_list.append(mobile)
        if trantype:
            query_params = "{} and t1.trantype=%s".format(query_params)
            query_list.append(trantype)
        if ordercode:
            query_params = "{} and t1.ordercode=%s".format(query_params)
            query_list.append(ordercode)
        value2=self.request.query_params.get('value2',None)
        if value2:
            query_params = "{} and t1.createtime>=%s and t1.createtime<=%s".format(query_params)
            query_list.append(string_toTimestamp(value2[:10]+' 00:00:01'))
            query_list.append(string_toTimestamp(value2[:10] + ' 23:59:59'))

        tranlist = Tranlist.objects.raw("""
                   SELECT t1.id,t1.tranname,t2.mobile,t3.mobile as mobile_to,t1.amount,t1.bal,t1.createtime,t1.ordercode
                   FROM `tranlist` as t1
                   LEFT  JOIN `user` as t2 on t1.userid = t2.userid
                   LEFT  JOIN `user` as t3 on t1.userid_to = t3.userid
                   WHERE 1=1 {} order by t1.createtime DESC
               """.format(query_params), query_list)
        print(tranlist)

        return {'data': TranlistQuerySerializer(tranlist, many=True).data}

    # @list_route(methods=['GET'])
    # @Core_connector(pagination=True)
    # def orderquery(self,request,*args,**kwargs):
    #     status=self.request.query_params.get('status',None)
    #     ordercode=self.request.query_params.get('ordercode',None)
    #     mobile=self.request.query_params.get('mobile',None)
    #     trantype=self.request.query_params.get('trantype',None)
    #
    #     if not status:
    #         raise PubErrorCustom("查询状态为空!")
    #
    #     query_params = str()
    #     query_list = list()
    #
    #     if status:
    #         query_params = "{} and t1.status=%s".format(query_params)
    #         query_list.append(status)
    #     if mobile:
    #         query_params = "{} and t2.mobile=%s".format(query_params)
    #         query_list.append(mobile)
    #     if ordercode:
    #         query_params = "{} and t1.ordercode=%s".format(query_params)
    #         query_list.append(ordercode)
    #     if trantype:
    #         query_params = "{} and t1.trantype=%s".format(query_params)
    #         query_list.append(trantype)
    #     order=Order.objects.raw("""
    #         SELECT t1.ordercode,t2.mobile,t3.mobile as mobile_to,t1.amount,t1.ordercode_to,t1.confirmtime,t1.img
    #         FROM `order` as t1
    #         INNER  JOIN `user` as t2 on t1.userid = t2.userid
    #         INNER  JOIN `user` as t3 on t1.userid_to = t3.userid
    #         WHERE 1=1 {} order by t1.createtime DESC
    #     """.format(query_params),query_list)
    #     print(order)
    #
    #     return {'data':OrderStatusSerializer(order,many=True).data}

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def orderquery(self,request,*args,**kwargs):
        status=self.request.query_params.get('status',None)
        ordercode=self.request.query_params.get('ordercode',None)
        mobile=self.request.query_params.get('mobile',None)
        ordercode_to=self.request.query_params.get('ordercode_to',None)
        mobile_to=self.request.query_params.get('mobile_to',None)

        if not status:
            raise PubErrorCustom("查询状态为空!")

        query_params = str()
        query_list = list()

        if status:
            query_params = "{} and t1.status=%s".format(query_params)
            query_list.append(status)
        if mobile:
            query_params = "{} and t2.mobile=%s".format(query_params)
            query_list.append(mobile)
        if ordercode:
            query_params = "{} and t1.ordercode=%s".format(query_params)
            query_list.append(ordercode)
        if mobile_to:
            query_params = "{} and t3.mobile=%s".format(query_params)
            query_list.append(mobile_to)
        if ordercode_to:
            query_params = "{} and t1.ordercode_to=%s".format(query_params)
            query_list.append(ordercode_to)

        value2=self.request.query_params.get('value2',None)
        if value2:
            if str(status)=='1':
                query_params = "{} and t1.matchtime>=%s and t1.matchtime<=%s".format(query_params)
            else:
                query_params = "{} and t1.confirmtime>=%s and t1.confirmtime<=%s".format(query_params)
            query_list.append(string_toTimestamp(value2[:10]+' 00:00:01'))
            query_list.append(string_toTimestamp(value2[:10] + ' 23:59:59'))

        print(query_params)
        print(query_list)

        order=Order.objects.raw("""
            SELECT t1.ordercode,t2.mobile,t3.mobile as mobile_to,t1.amount,t1.ordercode_to,t1.confirmtime,t1.img,t2.name,t3.name as name_to
            FROM `order` as t1
            INNER  JOIN `user` as t2 on t1.userid = t2.userid
            INNER  JOIN `user` as t3 on t1.userid_to = t3.userid
            WHERE t1.umark=0 and t1.trantype=0 {} order by t1.createtime DESC
        """.format(query_params),query_list)
        print(order)

        return {'data':OrderStatusSerializer(order,many=True).data}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def delorder(self,request,*args,**kwargs):

        Order.objects.filter(ordercode=self.request.data.get('ordercode')).update(umark=1)
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def matchadd(self, request, *args, **kwargs):

        order=Order.objects.filter(ordercode__in=request.data.get('ordercodes').split(','),umark=0)
        trantype=request.data.get('trantype')

        if trantype==0:
            trantype1=1
        else:
            trantype1=0

        usernames = list()
        r_usernames = list()
        order1 = Order.objects.raw("""
                   SELECT t1.*
                   FROM `order` as t1
                   INNER JOIN matchpool as t2 on t1.ordercode=t2.ordercode
                   where {}
               """.format('t1.trantype=%s and username in (select username from `order` where ordercode in %s)'),
                                  [trantype1, request.data.get('ordercodes').split(',')])
        for item in list(order1):
            usernames.append(item.username)

        if order.exists():
            for item in order:
                if MatchPool.objects.filter(ordercode=item.ordercode).count():
                    raise PubErrorCustom("添加重复！")
                if item.username in usernames:
                    r_usernames.append(item.username)
                    continue

                MatchPool.objects.create(ordercode=item.ordercode,trantype=trantype,flag=0)


        r_usernames=list(set(r_usernames))
        if len(r_usernames):
            msg="添加成功,用户重复部分,已剔除%s"%(str(r_usernames))
        else:
            msg="添加成功!"

        return {"data":'None','msg':msg}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def matchdel(self, request, *args, **kwargs):

        MatchPool.objects.filter(ordercode=request.data.get('ordercode')).delete()

        return None

    @list_route(methods=['GET'])
    @Core_connector()
    def matchquery(self, request, *args, **kwargs):

        trantype=self.request.query_params.get('trantype')
        query_params=str()
        query_list=list()

        if trantype :
            query_params = '{} and t2.trantype=%s'.format(query_params)
            query_list.append(trantype)

        order=Order.objects.raw(
            """
                SELECT t1.`ordercode`,t1.username,t1.amount,t1.createtime,t3.mobile
                FROM `order` as t1
                INNER JOIN `matchpool` as t2 ON t1.ordercode=t2.ordercode 
                INNER JOIN `user` as t3 ON t1.userid=t3.userid
                WHERE 1=1 and t1.status=0 and t2.flag=0 and t1.umark=0 {} ORDER BY t2.createtime desc
            """.format(query_params), query_list)
        order=list(order)

        return {'data': OrderSerializer1(order,many=True).data}

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def userquery(self,request, *args, **kwargs):

        username=self.request.query_params.get('username',None)
        name=self.request.query_params.get('name',None)
        referee_name=self.request.query_params.get('referee_name',None)
        userquery=Users.objects.all()
        if username:
            userquery=userquery.filter(username=username)
        if name:
            userquery=userquery.filter(name=name)
        if referee_name:
            userquery=userquery.filter(referee_name=referee_name)

        return {'data':UsersSerializer(userquery.order_by('-createtime'),many=True).data}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def userupd(self, request, *args, **kwargs):
        try:
            user=Users.objects.get(userid=request.data.get('userid'))
        except user.DoesNotExist:
            raise PubErrorCustom('用户不存在')
        if not request.data.get('passwd'):
            request.data['passwd']=user.passwd
        if not request.data.get('pay_passwd'):
            request.data['pay_passwd']=user.pay_passwd
        if not request.data.get('rcqlimit'):
            request.data['rcqlimit'] = 0

        if request.data.get('username') and request.data.get('username')!=user.username:
            if Users.objects.filter(username=request.data.get('username')).count():
                raise PubErrorCustom("该用户名已存在!")
            Order.objects.filter(userid=user.userid).update(username=request.data.get('username'))
            Order.objects.filter(userid_to=user.userid).update(username_to=request.data.get('username'))
            Tranlist.objects.filter(userid=user.userid).update(username=request.data.get('username'))
            Tranlist.objects.filter(userid_to=user.userid).update(username_to=request.data.get('username'))

        if request.data.get('mobile') and request.data.get('mobile') != user.mobile and request.data.get('referee_name') and request.data.get('referee_name')!=user.referee_name:
            raise PubErrorCustom("手机号和推荐人不能同时修改!")

        if request.data.get('mobile') and request.data.get('mobile')!=user.mobile:
            if Users.objects.filter(mobile=request.data.get('mobile')).count():
                raise PubErrorCustom("该手机号已存在!")
            Users.objects.filter(referee_name=user.mobile).update(referee_name=request.data.get('mobile'))
            Agent.objects.filter(mobile=user.mobile).update(mobile=request.data.get('mobile'))
            Agent.objects.filter(mobile1=user.mobile).update(mobile1=request.data.get('mobile'))
            Login.objects.filter(mobile=user.mobile).update(mobile=request.data.get('mobile'))

        print(request.data)
        if request.data.get('referee_name') and request.data.get('referee_name')!=user.referee_name:

            if request.data.get('referee_name') == user.mobile:
                raise PubErrorCustom("推荐人不能修改成自己!")

            if Users.objects.filter(mobile=request.data.get('referee_name')).count() == 0:
                raise PubErrorCustom("此推荐人不存在!")


            from apps.public.utils import query_agent_limit

            if query_agent_limit(user.mobile,request.data.get('referee_name')):
                raise PubErrorCustom("推荐人不能改成下级!")

            #修改自己的下级为推荐人的二级

            agent=Agent.objects.filter(mobile=user.mobile,level=1)
            if agent.exists():
                for item in agent:
                    Agent.objects.filter(mobile1=item.mobile1,level=2).update(mobile=request.data.get('referee_name'))

            #修改推荐人
            Agent.objects.filter(mobile1=user.mobile,level=1).update(mobile=request.data.get('referee_name'))

            Agent.objects.filter(mobile1=user.mobile,level=2).delete()

            #修改为推荐人的推荐人的二级
            try:
                agent=Agent.objects.get(mobile1=request.data.get('referee_name'),level=1)
                Agent.objects.create(
                    mobile=agent.mobile,
                    mobile1=user.mobile,
                    level=2
                )
            except Agent.DoesNotExist:
                pass

        serializer = UsersSerializer1(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def amountsend(self, request, *args, **kwargs):

        try:
            user=Users.objects.get(userid=request.data.get('userid'))
        except Users.DoesNotExist:
            raise  PubErrorCustom("该账号不存在")

        amount = request.data.get('amount')

        if str(request.data.get('type')) == '7':
            bal=user.bonus
            user.bonus += int(amount)
        elif str(request.data.get('type')) == '8':
            bal = user.spread
            user.spread += int(amount)
        elif str(request.data.get('type')) == '15':
            bal=user.activation
            user.activation += int(amount)
        elif str(request.data.get('type')) == '16':
            bal = user.buypower
            user.buypower += int(amount)
        elif str(request.data.get('type')) == '28':
            bal = user.integral
            user.integral += int(amount)
        else:
            raise PubErrorCustom("类型有误!")

        Tranlist.objects.create(
            trantype=request.data.get('type'),
            userid=user.userid,
            username=user.username,
            userid_to=user.userid,
            username_to=user.username,
            bal=bal,
            amount=int(amount)
        )
        user.save()
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def match(self, request, *args, **kwargs):

        t = time.mktime(timezone.now().timetuple())

        print("开始匹配")

        from django.core.cache import cache
        lock=cache.get('%s' % ('lock_match'))

        print("lock:",lock)

        if lock:
            raise PubErrorCustom("正在匹配,请稍后!")
        cache.set('%s'%('lock_match'), '1',timeout=None)

        try:
            from apps.serveradmin.utils import matchdata_get, matchcheck, matchexchange, match_core_handle, \
                match_upd_db, match_smssend, match_split
            #获取需匹配数据
            res=matchdata_get()

            #校验是否满足条件
            mobiles=matchcheck(res)

            #数据转换
            tgbz_obj,jsbz_obj,tgbz_split,jsbz_split=matchexchange(res)

            #核心处理
            install_orders,tgbz_split,jsbz_split=match_core_handle(tgbz_obj,jsbz_obj,t,tgbz_split,jsbz_split)

            #订单拆分
            match_split(tgbz_split,jsbz_split)

            #清理数据
            MatchPool.objects.filter().delete()

            #更新数据库
            # match_upd_db(install_orders)

            #发送短信
            match_smssend(mobiles)
            cache.delete('lock_match')
        except PubErrorCustom as e:
            cache.delete('lock_match')
            raise PubErrorCustom(e.msg)
        except Exception as e:
            cache.delete('lock_match')
            raise PubErrorCustom(str(e))
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def ordersplit(self, request, *args, **kwargs):
        amounts = request.data.get('amounts')
        ordercode = request.data.get('ordercode')

        if not ordercode:
            raise PubErrorCustom("订单号不能为空")

        if not(len(amounts.split(','))>1):
            raise PubErrorCustom("拆分格式错误！")

        try:
            order = Order.objects.get(ordercode=ordercode,umark=0)
        except Order.DoesNotExist:
            raise PubErrorCustom("无此订单!")

        if order.status != 0:
            raise PubErrorCustom("该状态不能拆分")

        sum = 0
        for item in amounts.split(','):
            sum += int(item)
        if order.amount != sum:
            raise PubErrorCustom("拆分金额与订单金额不匹配！")

        orders=list()
        for (index, item) in enumerate(amounts.split(',')):
            if index == 0:
                order.amount = item
                order.save()
                orders.append(order.ordercode)
            else:
                order1=Order.objects.create(**{
                    'trantype': order.trantype,
                    'subtrantype': order.subtrantype,
                    'amount': item,
                    'userid': order.userid,
                    'username': order.username,
                    'userid_to': order.userid_to,
                    'username_to': order.username_to,
                    'ordercode_to': order.ordercode_to,
                    'status': order.status,
                    'createtime': order.createtime,
                    'matchtime': order.matchtime,
                    'img': order.img
                })
                orders.append(order1.ordercode)
        tranname='订单拆分['
        for item in orders:
            tranname+="%s,"%str(item)
        tranname+=']'
        Tranlist.objects.create(**{
            'trantype': 24,
            'tranname':tranname,
            'userid':order.userid,
            'username':order.username,
            'ordercode':order.ordercode
        })

    @list_route(methods=['GET'])
    @Core_connector()
    def ordercount(self,request,*args,**kwargs):

        startdate=request.query_params.get('startdate',None)
        enddate=request.query_params.get('enddate',None)
        order=Order.objects.filter(umark=0)
        print(startdate,enddate)
        if startdate and enddate:
            startdate=string_toTimestamp(startdate)
            enddate=string_toTimestamp(enddate)
            order=order.filter(createtime__gte=startdate,createtime__lte=enddate)
        tgbzcount=0
        jsbzcount=0
        tgbztx=0
        jsbztx=0
        for item in order:
            if item.trantype == 0:
                tgbzcount+=item.amount
                if item.status==2:
                    tgbztx+=item.amount
            else:
                jsbzcount+=item.amount
                if item.status==2:
                    jsbztx+=item.amount

        return {'data':[{
            'tgbzcount':tgbzcount,
            'jsbzcount':jsbzcount,
            'tgbztx':tgbztx,
            'jsbztx':jsbztx
        }]}


    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def orderserverdel(self,request,*args,**kwargs):
        ordercodes=self.request.data.get('ordercodes',None)

        for ordercode in ordercodes.split(','):
            print(ordercode)
            try:
                order=Order.objects.get(ordercode=ordercode)
            except Order.DoesNotExist:
                raise PubErrorCustom("订单号不存在!")

            try:
                order_to=Order.objects.get(ordercode=order.ordercode_to)
            except Order.DoesNotExist:
                raise PubErrorCustom("对方订单号不存在!")

            order.umark=1
            order_to.umark=1
            order.save()
            order_to.save()

        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def tranlistserverdel(self,request,*args,**kwargs):
        ids=self.request.data.get('ids',None)

        for id in ids.split(','):
            print(id)
            Tranlist.objects.filter(id=id).delete()
        return None
