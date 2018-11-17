
from rest_framework import serializers
from apps.order.models import MatchPool

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


