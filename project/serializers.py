from rest_framework import serializers

from .models import IntelGroups
from .models import Plans


class IntelGroupSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(
    #     read_only=True,
    #     default=serializers.CurrentUserDefault()
    # )
    # department = serializers.ChoiceField(choices=Employee.DEPARTMENT_CHOICES)

    class Meta:
        model = IntelGroups
        fields = ('id', 'uniqueid', 'name', 'description', 'plan_id', 'created_at', 'updated_at')

class PlanSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(
    #     read_only=True,
    #     default=serializers.CurrentUserDefault()
    # )
    # department = serializers.ChoiceField(choices=Employee.DEPARTMENT_CHOICES)

    class Meta:
        model = Plans
        fields = ('id', 'type', 'name', 'annual_price', 'monthly_price', 'max_feeds', 'max_users', 'enable_custom_feeds', 'enable_api', 'enable_custom_extraction', 'created_at', 'updated_at')
