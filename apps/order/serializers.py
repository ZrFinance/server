


from rest_framework import serializers
from apps.order.models import Order,Tranlist
from utils.mytime import diff_day,timestamp_toDatetime,add_time
from apps.public.models import SysParam
from apps.user.models import Users

class OrderSerializer2(serializers.Serializer):

    mobile=serializers.CharField()
    alipay=serializers.CharField()
    wechat=serializers.CharField()
    bank=serializers.CharField()
    bank_account=serializers.CharField()
    referee_name=serializers.CharField()
    name=serializers.CharField()
    ordercode=serializers.IntegerField()
    stime = serializers.SerializerMethodField()
    status = serializers.IntegerField()
    img=serializers.CharField()
    updtime=serializers.IntegerField()

    def get_stime(self,obj):
        param=SysParam.objects.get()
        return add_time(obj.updtime,param.limit)

class OrderSerializer(serializers.ModelSerializer):
    username1=serializers.SerializerMethodField()
    username2=serializers.SerializerMethodField()
    updtime=serializers.SerializerMethodField()
    img=serializers.SerializerMethodField()
    name=serializers.SerializerMethodField()


    def name(self,obj):
        user=Users.objects.get(userid=obj.userid)
        return user.name

    def get_img(self,obj):
        if obj.trantype==0 and obj.status==1:
            return obj.img
        elif obj.trantype==1 and obj.status==1:
            order=Order.objects.get(ordercode=obj.ordercode_to,umark=0)
            return order.img
        else:
            return obj.img
    def get_username1(self,obj):
        if obj.trantype==0:
            return obj.username
        else:
            return obj.username_to

    def get_username2(self,obj):
        if obj.trantype==0:
            return obj.username_to
        else:
            return obj.username

    def get_updtime(self,obj):
        return obj.matchtime

    class Meta:
        model=Order
        fields='__all__'

class OrderSerializer1(serializers.Serializer):

    ordercode =serializers.IntegerField()
    mobile=serializers.CharField()
    username = serializers.CharField()
    mobile = serializers.CharField()
    amount = serializers.IntegerField()
    name = serializers.CharField()
    isday = serializers.SerializerMethodField()
    updtime = serializers.SerializerMethodField()
    registertime = serializers.IntegerField()

    def get_type(self,obj):
        if obj.status==0:
            return '等待中'
        elif obj.status==1:
            return '匹配成功'
        else:
            return '匹配成功'

    def get_istype(self,obj):
        if obj.status==0:
            return '未确认'
        elif obj.status==1:
            return '未确认'
        else:
            return '已确认收款'

    def get_isday(self,obj):
        return diff_day(timestamp_toDatetime(obj.createtime))

    def get_updtime(self,obj):
        return obj.createtime

class TranlistSerializer(serializers.ModelSerializer):
    tranname = serializers.CharField()
    bal = serializers.SerializerMethodField()
    def get_bal(self,obj):
        return 0

    class Meta:
        model=Tranlist
        fields='__all__'
