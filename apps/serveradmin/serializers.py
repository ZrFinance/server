
from rest_framework import serializers
from apps.order.models import MatchPool
from apps.public.models import SysParam
import time
from libs.utils.mytime import string_toTimestamp

class MatchPoolSerializer(serializers.ModelSerializer):
	class Meta:
		model=MatchPool
		fields='__all__'


class  OrderStatusSerializer(serializers.Serializer):
	ordercode=serializers.IntegerField()
	mobile=serializers.CharField()
	mobile_to=serializers.CharField()
	amount=serializers.IntegerField()
	ordercode_to=serializers.IntegerField()
	confirmtime=serializers.IntegerField()
	img=serializers.CharField()

class  TranlistQuerySerializer(serializers.Serializer):
	ordercode=serializers.IntegerField()
	mobile=serializers.CharField()
	mobile_to=serializers.CharField()
	amount=serializers.IntegerField()
	bal=serializers.IntegerField()
	createtime=serializers.IntegerField()
	tranname=serializers.CharField()


class  TranlistQuerySerializer1(serializers.Serializer):
	trantype=serializers.IntegerField()
	tranname=serializers.CharField()

class SysParamQuerySerializer(serializers.ModelSerializer):
	morning_time1=serializers.SerializerMethodField()
	morning_time2=serializers.SerializerMethodField()
	after_time1=serializers.SerializerMethodField()
	after_time2=serializers.SerializerMethodField()

	def get_morning_time1(self,obj):
		return time.strftime('%Y-%m-%d', time.localtime(time.time()))+' '+obj.morning.split('-')[0]

	def get_morning_time2(self,obj):
		return time.strftime('%Y-%m-%d', time.localtime(time.time()))+' '+obj.morning.split('-')[1]

	def get_after_time1(self,obj):
		return time.strftime('%Y-%m-%d', time.localtime(time.time()))+' '+obj.after.split('-')[0]

	def get_after_time2(self,obj):
		return time.strftime('%Y-%m-%d', time.localtime(time.time()))+' '+obj.after.split('-')[1]

	class Meta:
		model=SysParam
		fields='__all__'

