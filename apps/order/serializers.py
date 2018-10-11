


from rest_framework import serializers
from apps.order.models import Order,Tranlist

class OrderSerializer(serializers.ModelSerializer):
	class Meta:
		model=Order
		fields='__all__'

class TranlistSerializer(serializers.ModelSerializer):
	trantype = serializers.SerializerMethodField()
	bal = serializers.SerializerMethodField()

	def get_trantype(self,obj):
		if obj.trantype == 1:
			trantype = '转出{}'.format(obj.username_to)
		elif obj.trantype == 2:
			trantype = '{}转入'.format(obj.username_to)
		elif obj.trantype == 3:
			trantype = '幸运排单消耗'
		elif obj.trantype == 4:
			trantype = '转出{}'.format(obj.username_to)
		elif obj.trantype == 5:
			trantype = '{}转入'.format(obj.username_to)
		return trantype
	def get_bal(self,obj):
		return 0

	class Meta:
		model=Tranlist
		fields='__all__'
