


from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from apps.user.models import Users,Agent
from include.data import choices_list

from apps.order.models import Order


class UsersSerializer1(serializers.ModelSerializer):

	class Meta:
		model=Users
		fields='__all__'

		validators = [
			UniqueTogetherValidator(
				queryset=Users.objects.all(),
				fields=('mobile',),
				message="手机号重复！"
			),
		]


class UsersSerializer(serializers.ModelSerializer):
	pay_passwd = serializers.SerializerMethodField()
	passwd = serializers.SerializerMethodField()
	statusname = serializers.SerializerMethodField()
	endtime = serializers.SerializerMethodField()

	def get_statusname(self,obj):
		if obj.status==0:
			return '正常'
		elif obj.status==1:
			return '未激活'
		else:
			return '禁用'

	def get_endtime(self,obj):
		order=Order.objects.filter(userid=obj.userid,umark=0).order_by('-createtime').values('createtime')
		if order.exists():
			return order[0]['createtime']

		return ''

	def get_pay_passwd(self,obj):
		return ''

	def get_passwd(self,obj):
		return ''

	class Meta:
		model=Users
		fields='__all__'

		validators = [
			UniqueTogetherValidator(
				queryset=Users.objects.all(),
				fields=('mobile',),
				message="手机号重复！"
			),
		]

class AgentModelSerializer(serializers.ModelSerializer):
	class Meta:
		model=Agent
		fields='__all__'


class AgentSerializer(serializers.Serializer):
	id=serializers.IntegerField()
	mobile=serializers.CharField()
	createtime=serializers.IntegerField()
	status=serializers.SerializerMethodField()

	def get_status(self,obj):
		a=lambda x: [item[1] for item in choices_list.user_status if int(x) == item[0]][0]
		return a(obj.status)