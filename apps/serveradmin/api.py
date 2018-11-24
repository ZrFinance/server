
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

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def tgbzquery(self, request,*args,**kwargs):
        flag=self.request.query_params.get('flag',None)
        mobile=self.request.query_params.get('mobile',None)
        amount=self.request.query_params.get('amount',None)
        day = self.request.query_params.get('day', 2)

        query_params = str()
        query_list = list()

        if mobile:
            query_params = "{} and t2.mobile=%s".format(query_params)
            query_list.append(mobile)
        if amount:
            query_params = "{} and t1.amount=%s".format(query_params)
            query_list.append(amount)

        order=Order.objects.raw(
            """
                SELECT t1.`ordercode`,t2.mobile,t1.amount,t2.name,t1.createtime,t1.status
                FROM `order` as t1
                INNER JOIN `user` as t2 ON t1.userid=t2.userid 
                WHERE 1=1 and t1.status=0 and trantype=0 and t1.umark=0 {} ORDER BY createtime desc
            """.format(query_params), query_list)
        order=list(order)

        if flag:
            data=[]
            order1=Order.objects.raw(
                """
                    SELECT t1.ordercode,t1.userid,count(1) as count
                    FROM `order` as t1
                    INNER JOIN `user` as t2 ON t1.userid=t2.userid 
                    WHERE 1=1 and t1.status=0 and trantype=0 and t1.umark=0 group by t1.userid
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
        if int(day)==1:
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

        query_params = str()
        query_list = list()

        if mobile:
            query_params = "{} and t2.mobile=%s".format(query_params)
            query_list.append(mobile)
        if amount:
            query_params = "{} and t1.amount=%s".format(query_params)
            query_list.append(amount)

        order=Order.objects.raw(
            """
                SELECT t1.`ordercode`,t2.mobile,t1.amount,t2.name,t1.createtime,t1.status
                FROM `order` as t1
                INNER JOIN `user` as t2 ON t1.userid=t2.userid 
                WHERE 1=1 and t1.status=0 and trantype=1 and t1.umark=0 {} ORDER BY createtime desc
            """.format(query_params), query_list)
        order=list(order)

        if flag:
            data=[]
            order1=Order.objects.raw(
                """
                    SELECT t1.ordercode,t1.userid,count(1) as count
                    FROM `order` as t1
                    INNER JOIN `user` as t2 ON t1.userid=t2.userid 
                    WHERE 1=1 and t1.status=0 and trantype=1 and t1.umark=0 group by t1.userid
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
        if int(day)==1:
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
        trantype=self.request.query_params.get('trantype',None)

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
        if trantype:
            query_params = "{} and t1.trantype=%s".format(query_params)
            query_list.append(trantype)
        order=Order.objects.raw("""
            SELECT t1.ordercode,t2.mobile,t3.mobile as mobile_to,t1.amount,t1.ordercode_to,t1.confirmtime,t1.img
            FROM `order` as t1
            INNER  JOIN `user` as t2 on t1.userid = t2.userid
            INNER  JOIN `user` as t3 on t1.userid_to = t3.userid
            WHERE t1.umark=0 {} order by t1.createtime DESC
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
        if order.exists():
            for item in order:
                if MatchPool.objects.filter(ordercode=item.ordercode).count():
                    raise PubErrorCustom("添加重复！")
                MatchPool.objects.create(ordercode=item.ordercode,trantype=trantype,flag=0)

        return None

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
        userquery=Users.objects.all()
        if username:
            userquery=userquery.filter(username=username)
        if name:
            userquery=userquery.filter(name=name)

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
            Tranlist.objects.create(
                trantype=request.data.get('type'),
                userid=user.userid,
                username=user.username,
                bal=user.bonus,
                amount=int(amount)
            )
            user.bonus += int(amount)
        elif str(request.data.get('type')) == '8':
            Tranlist.objects.create(
                trantype=request.data.get('type'),
                userid=user.userid,
                username=user.username,
                bal=user.spread,
                amount=int(amount)
            )
            user.spread += int(amount)
        elif str(request.data.get('type')) == '15':
            Tranlist.objects.create(
                trantype=request.data.get('type'),
                userid=user.userid,
                username=user.username,
                bal=user.activation,
                amount=int(amount)
            )
            user.activation += int(amount)
        elif str(request.data.get('type')) == '16':
            Tranlist.objects.create(
                trantype=request.data.get('type'),
                userid=user.userid,
                username=user.username,
                bal=user.buypower,
                amount=int(amount)
            )
            user.buypower += int(amount)
        elif str(request.data.get('type')) == '28':
            Tranlist.objects.create(
                trantype=request.data.get('type'),
                userid=user.userid,
                username=user.username,
                bal=user.integral,
                amount=int(amount)
            )
            user.integral += int(amount)
        user.save()
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def match(self, request, *args, **kwargs):

        print("match start...")
        match1=list(Order.objects.raw(
            """
                SELECT t1.*
                FROM `order` as t1
                INNER JOIN `matchpool` as t2 ON t1.ordercode = t2.ordercode
                WHERE t2.trantype=0 and t2.flag=0 order by t1.amount
            """
        ))

        match2=list(Order.objects.raw(
            """
                SELECT t1.*
                FROM `order` as t1
                INNER JOIN `matchpool` as t2 ON t1.ordercode = t2.ordercode
                WHERE t2.trantype=1 and t2.flag=0 order by t1.amount
            """
        ))

        t = time.mktime(timezone.now().timetuple())
        sum1=0
        sum2=0
        for item in match1:
            sum1 += item.amount
        for item in match2:
            sum2 += item.amount

        if sum1 != sum2 :
            raise PubErrorCustom("金额不匹配！")

        if sum1==0 or sum2==0:
            raise PubErrorCustom('无匹配对象')

        inner_value1=list()
        index_list1=list()
        index_list2=list()
        for (index1,item) in enumerate(match1):
            for (index2,item1) in enumerate(match2):
                if item.amount == item1.amount and item1.ordercode not in inner_value1:
                    Order.objects.filter(ordercode=item.ordercode).update(status=1,userid_to=item1.userid,username_to=item1.username,ordercode_to=item1.ordercode,matchtime=t)
                    Order.objects.filter(ordercode=item1.ordercode).update(status=1, userid_to=item.userid,username_to=item.username,ordercode_to=item.ordercode,matchtime=t)
                    inner_value1.append(item1.ordercode)
                    index_list2.append(index2)
                    index_list1.append(index1)
                    break
        index_list1.sort(reverse=True)
        index_list2.sort(reverse=True)
        for item in index_list1:
            del(match1[item])
        for item in index_list2:
            del(match2[item])

        tgbz_obj = list()
        jsbz_obj = list()
        inner_value = list()
        index = 0
        while True:
            obj1=match1[index] if len(match1)-1>=index else None
            obj2=match2[index] if len(match2)-1>=index else None
            index+=1
            if not obj1 and not obj2:
                break

            amountobj1 = 0 if not obj1 else obj1.amount
            amountobj2 = 0 if not obj2 else obj2.amount

            amount=amountobj1 - amountobj2
            if amount < 0:

                tmpamount = amount * -1
                if not len(tgbz_obj):
                    if obj1 and obj2:
                        Order.objects.filter(ordercode=obj1.ordercode).update(status=1, userid_to=obj2.userid,
                                                                          username_to=obj2.username,ordercode_to=obj2.ordercode,matchtime=t)
                        Order.objects.filter(ordercode=obj2.ordercode).update(status=1, userid_to=obj1.userid,
                                                                           username_to=obj1.username,ordercode_to=obj1.ordercode,matchtime=t)
                else:
                    if obj1 and obj2:
                        Order.objects.filter(ordercode=obj1.ordercode).update(status=1, userid_to=obj2.userid,
                                                                          username_to=obj2.username,amount=amountobj1,ordercode_to=obj2.ordercode,matchtime=t)
                        Order.objects.filter(ordercode=obj2.ordercode).update(status=1, userid_to=obj1.userid,
                                                                           username_to=obj1.username,amount=amountobj1,ordercode_to=obj1.ordercode,matchtime=t)
                    for item in tgbz_obj:
                        if item['obj'].ordercode in inner_value:
                            continue
                        if tmpamount >= item['amount']:
                            order=Order.objects.get(ordercode=obj2.ordercode)
                            order.status=1
                            order.userid_to=item['obj'].userid
                            order.username_to=item['obj'].username
                            order.amount=item['amount']
                            order.ordercode_to=item['obj'].ordercode
                            order.matchtime = t
                            order.save()

                            s=Order.objects.get(ordercode=item['obj'].ordercode)
                            s.ordercode_to = "{},{}".format(s.ordercode_to,order.ordercode)
                            s.username_to= "{},{}".format(s.username_to,order.username)
                            s.userid_to = "{},{}".format(s.userid_to, order.userid)
                            s.matchtime = t
                            s.save()
                            tmpamount -= item['amount']
                            inner_value.append(item['obj'].ordercode)
                            if tmpamount == 0 :
                                break
                        else:
                            order=Order.objects.get(ordercode=obj2.ordercode)
                            order.status=1
                            order.userid_to=item['obj'].userid
                            order.username_to=item['obj'].username
                            order.amount=tmpamount
                            order.ordercode_to=item['obj'].ordercode
                            order.matchtime = t
                            order.save()

                            s=Order.objects.get(ordercode=item['obj'].ordercode)
                            s.ordercode_to = "{},{}".format(s.ordercode_to,order.ordercode)
                            s.username_to= "{},{}".format(s.username_to,order.username)
                            s.userid_to = "{},{}".format(s.userid_to, order.userid)
                            s.matchtime = t
                            s.save()
                            item['amount'] -= tmpamount
                            tmpamount=0
                            break
                if tmpamount:
                        jsbz_obj.append({
                            'amount': tmpamount,
                            'obj':obj2
                        })
            else:
                tmpamount = amount
                if not len(jsbz_obj):
                    if obj1 and obj2:
                        Order.objects.filter(ordercode=obj1.ordercode).update(status=1, userid_to=obj2.userid,
                                                                          username_to=obj2.username,ordercode_to=obj2.ordercode,matchtime=t)
                        Order.objects.filter(ordercode=obj2.ordercode).update(status=1, userid_to=obj1.userid,
                                                                           username_to=obj1.username,ordercode_to=obj1.ordercode,matchtime=t)
                else:
                    if obj1 and obj2 :
                            Order.objects.filter(ordercode=obj1.ordercode).update(status=1, userid_to=obj2.userid,
                                                                              username_to=obj2.username,amount=amountobj2,ordercode_to=obj2.ordercode,matchtime=t)
                            Order.objects.filter(ordercode=obj2.ordercode).update(status=1, userid_to=obj1.userid,
                                                                               username_to=obj1.username,amount=amountobj2,ordercode_to=obj1.ordercode,matchtime=t)
                    for item in jsbz_obj:
                        if item['obj'].ordercode in inner_value:
                            continue
                        if tmpamount >= item['amount']:
                            order=Order.objects.get(ordercode=obj1.ordercode)
                            order.status=1
                            order.userid_to=item['obj'].userid
                            order.username_to=item['obj'].username
                            order.amount=item['amount']
                            order.ordercode_to=item['obj'].ordercode
                            order.matchtime = t
                            order.save()

                            s=Order.objects.get(ordercode=item['obj'].ordercode)
                            s.ordercode_to = "{},{}".format(s.ordercode_to,order.ordercode)
                            s.username_to= "{},{}".format(s.username_to,order.username)
                            s.userid_to = "{},{}".format(s.userid_to, order.userid)
                            s.matchtime = t
                            s.save()
                            tmpamount -= item['amount']
                            inner_value.append(item['obj'].ordercode)
                            if tmpamount == 0 :
                                break
                        else:
                            order=Order.objects.get(ordercode=obj1.ordercode)
                            order.status=1
                            order.userid_to=item['obj'].userid
                            order.username_to=item['obj'].username
                            order.amount=tmpamount
                            order.ordercode_to=item['obj'].ordercode
                            order.matchtime = t
                            order.save()

                            s=Order.objects.get(ordercode=item['obj'].ordercode)
                            s.ordercode_to = "{},{}".format(s.ordercode_to,order.ordercode)
                            s.username_to= "{},{}".format(s.username_to,order.username)
                            s.userid_to = "{},{}".format(s.userid_to, order.userid)
                            s.matchtime = t
                            s.save()
                            item['amount'] -= tmpamount
                            tmpamount=0
                            break
                if tmpamount:
                    tgbz_obj.append({
                        'amount': tmpamount,
                        'obj':obj1
                    })


        match1=list(Order.objects.raw(
            """
                SELECT t1.*
                FROM `order` as t1
                INNER JOIN `matchpool` as t2 ON t1.ordercode = t2.ordercode
                WHERE t2.trantype=0 and t2.flag=0 and t1.umark=0 order by t1.amount
            """
        ))

        match2=list(Order.objects.raw(
            """
                SELECT t1.*
                FROM `order` as t1
                INNER JOIN `matchpool` as t2 ON t1.ordercode = t2.ordercode
                WHERE t2.trantype=1 and t2.flag=0 and t1.umark=0 order by t1.amount
            """
        ))

        for item in match1:
            ordercodes=item.ordercode_to.split(',')
            if len(ordercodes)<=1:
                continue
            else:
                for (index,ordercode) in enumerate(ordercodes):
                    if index==0:
                        s=Order.objects.get(ordercode=ordercode)
                        Order.objects.filter(ordercode=item.ordercode).update(amount=s.amount,userid_to=s.userid,username_to=s.username,ordercode_to=s.ordercode,matchtime=t)
                    else:
                        s = Order.objects.get(ordercode=ordercode)
                        p=Order.objects.create(**{
                            'trantype':item.trantype,
                            'subtrantype':item.trantype,
                            'amount':s.amount,
                            'userid':item.userid,
                            'username':item.username,
                            'userid_to':s.userid,
                            'username_to':s.username,
                            'ordercode_to':s.ordercode,
                            'status':item.status,
                            'createtime':item.createtime,
                            'matchtime':t
                        })
                        s.ordercode_to=p.ordercode
                        s.save()

                        MatchPool.objects.create(**{
                            'ordercode':p.ordercode,
                            'trantype':0,
                            'flag':0
                        })
        for item in match2:
            ordercodes=item.ordercode_to.split(',')
            if len(ordercodes)<=1:
                continue
            else:
                for (index,ordercode) in enumerate(ordercodes):
                    if index==0:
                        s=Order.objects.get(ordercode=ordercode)
                        Order.objects.filter(ordercode=item.ordercode).update(amount=s.amount,userid_to=s.userid,username_to=s.username_to,ordercode_to=s.ordercode,matchtime=t)
                    else:
                        s = Order.objects.get(ordercode=ordercode)
                        p=Order.objects.create(**{
                            'trantype':item.trantype,
                            'subtrantype':item.trantype,
                            'amount':s.amount,
                            'userid':item.userid,
                            'username':item.username,
                            'userid_to':s.userid,
                            'username_to':s.username,
                            'ordercode_to':s.ordercode,
                            'status':item.status,
                            'createtime':item.createtime,
                            'matchtime':t
                        })
                        s.ordercode_to=p.ordercode
                        s.save()

                        MatchPool.objects.create(**{
                            'ordercode':p.ordercode,
                            'trantype':1,
                            'flag':0
                        })

        MatchPool.objects.filter(trantype=0, flag=0).update(flag=1,matchtime=t)
        MatchPool.objects.filter(trantype=1, flag=0).update(flag=1,matchtime=t)

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
            if item.trantype == 1:
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


