


from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from apps.user.models import Users,Agent
from include.data import choices_list


class UsersSerializer(serializers.ModelSerializer):
	pay_passwd = serializers.SerializerMethodField()
	passwd = serializers.SerializerMethodField()

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