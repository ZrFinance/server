


from rest_framework import serializers
from apps.public.models import Verification,Lucky

class VerificationSerializer(serializers.ModelSerializer):
	class Meta:
		model=Verification
		fields='__all__'

class LuckySerializer(serializers.ModelSerializer):
	class Meta:
		model=Lucky
		fields=('name','createtime')


