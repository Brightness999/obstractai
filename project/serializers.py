from rest_framework import serializers
import json

from .models import IntelGroups, Plans, UserIntelGroupRoles, Categories, Tags, Feeds, Extractions, Indicators, Whitelists, APIKeys, WebHooks, FeedChannels, FeedItems, GlobalIndicators
from apps.users.models import CustomUser


class IntelGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = IntelGroups
        fields = ('id', 'uniqueid', 'name', 'description', 'plan_id', 'created_at', 'updated_at')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email','last_login')

class UserIntelGroupRolesSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = UserIntelGroupRoles
        fields = ('id', 'user_id', 'intelgroup_id', 'role', 'user')

class RoleGroupSerializer(serializers.ModelSerializer):
    intelgroup = IntelGroupSerializer(many=False, read_only=True)
    class Meta:
        model = UserIntelGroupRoles
        fields = ('id', 'user_id', 'intelgroup_id', 'role','intelgroup')

class PlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = Plans
        fields = ('id', 'types', 'name', 'annual_price', 'monthly_price', 'max_feeds', 'max_users', 'enabled_custom_feeds', 'enabled_api', 'enabled_custom_extraction', 'created_at', 'updated_at')

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Categories
        fields = ('__all__' )

class FeedCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)
    class Meta:
        model = Feeds
        fields = ('id', 'name', 'category_id', 'description', 'tags', 'url', 'confidence', 'manage_enabled', 'intelgroup_id','updated_at', 'category', 'uniqueid' )
    def add(self, instance, validated_data):
        instance.category_id = validated_data.get('category', instance.category_id)
        return instance
class FeedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Feeds
        fields = ('__all__' )


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = '__all__'

class GroupPlanSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(many=False, read_only=True)
    class Meta:
        model = IntelGroups
        fields = fields = ('id', 'uniqueid', 'name', 'description', 'plan_id', 'created_at', 'updated_at', 'plan')


class Comment:
    def __init__(self, name, description, userids):
        self.name = name
        self.description = description
        self.userids = userids
        self.data = data

class CommentSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=100)
    userids = serializers.ListField(
        child = serializers.IntegerField()
    )

class UsersInvitationSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    userids = serializers.ListField(
        child = serializers.IntegerField()
    )

class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tags
        fields = ('id', 'name', 'user_id', 'state')

class GlobalIndicatorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = GlobalIndicators
        fields = ('id', 'type', 'type_api', 'value', 'value_api', 'enabled')

class UserExtractionSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Extractions
        fields = ('id', 'types', 'value', 'words_matched', 'user_id', 'intelgroup_id', 'enabled', 'user')


class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicators
        fields = ('id', 'globalindicator_id', 'feeditem_id', 'enabled', 'value')

class UserIndicatorWhitelistSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    indicator = IndicatorSerializer(many=False)
    class Meta:
        model = Whitelists
        fields = ('id', 'value', 'indicator_id', 'user_id', 'enabled', 'user', 'indicator')

class APIKeySerializer(serializers.ModelSerializer):

    class Meta:
        model = APIKeys
        fields = ('id', 'name', 'value', 'user_id', 'intelgroup_id')

class GroupAPIkeySerializer(serializers.ModelSerializer):
    intelgroup = IntelGroupSerializer(many=False)
    class Meta:
        model = APIKeys
        fields = ('id', 'name', 'value', 'user_id', 'intelgroup_id', 'intelgroup')

class WebHookSerializer(serializers.ModelSerializer):

    class Meta:
        model = WebHooks
        fields = ('id', 'endpoint', 'description', 'user_id', 'intelgroup_id' )

class GroupWebHookSerializer(serializers.ModelSerializer):
    intelgroup = IntelGroupSerializer(many=False, read_only=True)
    class Meta:
        model = WebHooks
        fields = ('id', 'endpoint', 'description', 'user_id', 'intelgroup_id', 'intelgroup' )

class FeedChannelSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeedChannels
        fields = ('__all__')

class FeedItemSerializer(serializers.ModelSerializer):
    feed = FeedCategorySerializer(many=False, read_only=True)
    class Meta:
        model = FeedItems
        fields =('__all__')

class ItemIndicatorSerializer(serializers.ModelSerializer):
    feeditem = FeedItemSerializer(many=False, read_only=True)
    globalindicator = GlobalIndicatorSerializer(many=False, read_only=True)
    class Meta:
        model = Indicators
        fields = ('id', 'feeditem_id', 'enabled', 'globalindicator_id', 'value', 'feeditem', 'globalindicator')



class UserGlobalIndicatorSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(many=False, read_only=True)
    class Meta:
        model = GlobalIndicators
        fields = ('id', 'type', 'type_api', 'value', 'value_api', 'enabled', 'user')

class IndicatorGlobalSerializer(serializers.ModelSerializer):
    globalindicator = GlobalIndicatorSerializer(many=False, read_only=True)
    class Meta:
        model = Indicators
        fields = ('id', 'value', 'enabled', 'feeditem_id', 'globalindicator_id', 'globalindicator' )
