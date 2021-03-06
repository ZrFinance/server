
from rest_framework import viewsets
from rest_framework.decorators import list_route
from core.decorator.response import Core_connector
from utils.exceptions import PubErrorCustom

from apps.order.models import Order,Tranlist
from auth.authentication import Authentication
from apps.order.serializers import OrderSerializer

from apps.public.models import SysParam

from apps.utils import GenericViewSetCustom
from apps.public.utils import daysqbzcount,get_agent_totle_1,check_input_order

from apps.user.models import Agent,Users

from libs.utils.log import logger

class OrderAPIView(GenericViewSetCustom):

    def get_authenticators(self):
        return [auth() for auth in [Authentication]]

    @list_route(methods=['GET'])
    @Core_connector()
    def orderquery(self, request,*args,**kwargs):
        user = request.user
        trantype=self.request.query_params.get('trantype',None)
        status=self.request.query_params.get('status',None)

        if not trantype:
            raise PubErrorCustom("trantype是空!")

        print("trantype:",trantype,"userid:",user.userid)
        if str(trantype) == '0' or str(trantype) == '1':
            orderfilter = Order.objects.filter(userid=user.userid, trantype=trantype,status__in=[0,1],umark=0).order_by('-confirmtime','-matchtime','-createtime')
        elif str(trantype) == '2' :
            orderfilter = Order.objects.filter(userid=user.userid, status=2,umark=0).order_by('-confirmtime')
        else:
            raise PubErrorCustom("trantype非法!")

        return {'data':OrderSerializer(orderfilter,many=True).data}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def orderadd(self,request,*args,**kwargs):
        user = request.user
        sysparam=SysParam.objects.get()

        if user.pay_passwd != request.data.get('pay_passwd'):
            raise PubErrorCustom('二级密码错误！')

        if daysqbzcount(user.userid,sysparam):
            raise PubErrorCustom("当天申请帮助次数已超！")

        print("[%s]"%(str(request.data)))

        if request.data.get('defaultValue')=='gffh':
            if int(request.data.get('amount')) < sysparam.amount1 :
                raise PubErrorCustom('小于最低额%d'%(sysparam.amount1))
            if int(request.data.get('amount')) % sysparam.amount2 > 0:
                raise PubErrorCustom('必须为%d倍数'%(sysparam.amount2))
            if int(request.data.get('amount')) > sysparam.amount3:
                raise PubErrorCustom('高于最高额%d' % (sysparam.amount3))
            if user.bonus < int(request.data.get('amount')):
                raise PubErrorCustom("股份分红余额不足")
            type=2
            trantype=12
        else:
            # if int(request.data.get('amount')) < sysparam.amount4 :
            #     raise PubErrorCustom('小于最低额%d'%(sysparam.amount4))
            # if int(request.data.get('amount')) % sysparam.amount5 > 0:
            #     raise PubErrorCustom('必须为%d倍数'%(sysparam.amount5))
            if int(request.data.get('amount')) > sysparam.amount6:
                raise PubErrorCustom('高于最高额%d' % (sysparam.amount6))
            if user.spread < int(request.data.get('amount')):
                raise  PubErrorCustom('推广股权余额不足')

            agent_totle=get_agent_totle_1(user.mobile)

            def is_ok(count):
                t=0
                for item in agent_totle:
                    if item >= count :
                        t+=1
                return t

            if check_input_order(user.mobile):
                if is_ok(160) >=2 :
                    if int(request.data.get('amount')) > 2000:
                        raise PubErrorCustom("您两个区分别有%d人,只能提现最多2000"%(160))
                elif is_ok(80) >=2 :
                    if int(request.data.get('amount')) > 1200:
                        raise PubErrorCustom("您两个区分别有%d人,只能提现最多1200"%(80))
                elif is_ok(40) >=2 :
                    if int(request.data.get('amount')) > 800:
                        raise PubErrorCustom("您两个区分别有%d人,只能提现最多800"%(40))
                elif is_ok(20) >=2 :
                    if int(request.data.get('amount')) > 500:
                        raise PubErrorCustom("您两个区分别有%d人,只能提现最多500"%(20))
                elif is_ok(10) >=2 :
                    if int(request.data.get('amount')) > 300:
                        raise PubErrorCustom("您两个区分别有%d人,只能提现最多300"%(10))
                else:
                    raise PubErrorCustom("您两个区不足10人,不能提现")
            else:
                raise PubErrorCustom("需要直推3人才能提现")

            # #必须满足推荐人才能提取，1代2个提50%,2代4个提100%(必须满足1代)
            # oneagent=Agent.objects.filter(mobile=user.mobile,level=1)
            # oneagentcount=0
            # for item in oneagent:
            #     t=Order.objects.raw("""
            #         SELECT t1.ordercode FROM `order` as t1
            #         INNER JOIN user as t2 on t1.userid=t2.userid
            #         where t1.trantype='0' and t1.umark='0' and t1.status='2' and t2.status='0' and %s
            #     """%(" t2.mobile=%s"),[item.mobile1])
            #     t=list(t)
            #     if len(t)>0:
            #         oneagentcount+=1
            #
            # twoagent=Agent.objects.filter(mobile=user.mobile,level=2)
            # twoagentcount=0
            #
            # for item in twoagent:
            #     t=Order.objects.raw("""
            #         SELECT t1.ordercode FROM `order` as t1
            #         INNER JOIN user as t2 on t1.userid=t2.userid
            #         where t1.trantype='0' and t1.umark='0' and t1.status='2' and t2.status='0' and %s
            #     """%(" t2.mobile=%s"),[item.mobile1])
            #     t=list(t)
            #     if len(t)>0:
            #         twoagentcount+=1
            # if oneagentcount>=2 and twoagentcount>=4:
            #     pass
            #     #提取全部
            # elif oneagentcount<2:
            #     raise PubErrorCustom("一代不足2人,不能提取!")
            # else:
            #     if int(request.data.get('amount')) > user.spread / 2.0:
            #         raise PubErrorCustom("满足一代2人,二代4人能提取100%,否则提取50%")

            # if user.integral < 200:
            #     if int(request.data.get('amount')) > 500:
            #         raise PubErrorCustom('诚心值积分不够！')
            # elif user.integral < 320:
            #     if int(request.data.get('amount')) > 1000:
            #         raise PubErrorCustom('诚心值积分不够！')
            # elif user.integral < 440:
            #     if int(request.data.get('amount')) > 1500:
            #         raise PubErrorCustom('诚心值积分不够！')
            # elif user.integral < 560:
            #     if int(request.data.get('amount')) > 2000:
            #         raise PubErrorCustom('诚心值积分不够！')
            # elif user.integral < 760:
            #     if int(request.data.get('amount')) > 2500:
            #         raise PubErrorCustom('诚心值积分不够！')
            # elif user.integral < 960:
            #     if int(request.data.get('amount')) > 3000:
            #         raise PubErrorCustom('诚心值积分不够！')
            # elif user.integral < 1160:
            #     if int(request.data.get('amount')) > 3500:
            #         raise PubErrorCustom('诚心值积分不够！')
            # elif user.integral < 1560:
            #     if int(request.data.get('amount')) > 4000:
            #         raise PubErrorCustom('诚心值积分不够！')
            # elif user.integral < 2000:
            #     if int(request.data.get('amount')) > 5000:
            #         raise PubErrorCustom('诚心值积分不够！')
            # elif user.integral < 2500:
            #     if int(request.data.get('amount')) > 7000:
            #         raise PubErrorCustom('诚心值积分不够！')
            # else:
            #     if int(request.data.get('amount')) > 10000:
            #         raise PubErrorCustom('诚心值积分不够！')
            type=1
            trantype=11
        Order.objects.create(
            trantype=1,
            subtrantype=type,
            amount=request.data.get('amount'),
            userid=user.userid,
            username=user.username,
            status=0
        )

        if trantype==12:
            Tranlist.objects.create(
                trantype=trantype,
                userid=user.userid,
                username=user.username,
                bal=user.bonus,
                amount=int(request.data.get('amount'))*-1
            )
            user.bonus -= int(request.data.get('amount'))
        else:
            Tranlist.objects.create(
                trantype=trantype,
                userid=user.userid,
                username=user.username,
                bal=user.spread,
                amount=int(request.data.get('amount'))*-1
            )
            user.spread -= int(request.data.get('amount'))
        user.save()
        return None
