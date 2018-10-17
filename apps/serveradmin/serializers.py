
from rest_framework import serializers
from apps.order.models import MatchPool

class MatchPoolSerializer(serializers.ModelSerializer):
	class Meta:
		model=MatchPool
		fields='__all__'




