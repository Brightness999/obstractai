from rest_framework import serializers
import json

from djstripe.models import Product, Plan, Subscription
from .models import IntelGroups, UserIntelGroupRoles, Categories, Tags, Feeds, Indicators, Whitelists, APIKeys, GroupFeeds, \
    WebHooks, FeedChannels, FeedItems, GlobalIndicators, GlobalAttributes, Attributes, IntelReports, GroupGlobalAttributes
from apps.users.models import CustomUser

class IntelGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = IntelGroups
        fields = ('__all__')

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('__all__')

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Categories
        fields = ('__all__' )

class FeedSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Feeds
        fields = ('__all__' )

class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tags
        fields = ('__all__')

class GlobalIndicatorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = GlobalIndicators
        fields = ('id', 'type', 'type_api', 'value', 'value_api')

class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicators
        fields = ('id', 'globalindicator_id', 'feeditem_id', 'isenable', 'value')

class APIKeySerializer(serializers.ModelSerializer):

    class Meta:
        model = APIKeys
        fields = ('id', 'name', 'value', 'user_id', 'intelgroup_id')

class WebHookSerializer(serializers.ModelSerializer):

    class Meta:
        model = WebHooks
        fields = ('id', 'endpoint', 'description', 'user_id', 'intelgroup_id' )


class IntelReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = IntelReports
        fields = ('__all__')

class GlobalAttributeSerializer(serializers.ModelSerializer):

    class Meta:
        model = GlobalAttributes
        fields = ('__all__')

class GroupCategoryFeedSerializer(serializers.ModelSerializer):
    feed = FeedSerializer(many=False, read_only=True)
    intelgroup = IntelGroupSerializer(many=False, read_only=True)
    category = CategorySerializer(many=False, read_only=True)
    class Meta:
        model = GroupFeeds
        fields = ('__all__')

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

class UserGroupRoleSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    intelgroup = IntelGroupSerializer(many=False, read_only=True)
    class Meta:
        model = UserIntelGroupRoles
        fields = ('id', 'user_id', 'intelgroup_id', 'role', 'user', 'intelgroup')

class GroupRoleSerializer(serializers.ModelSerializer):
    intelgroup = IntelGroupSerializer(many=False, read_only=True)
    class Meta:
        model = UserIntelGroupRoles
        fields = ('id', 'role', 'intelgroup_id', 'intelgroup')

class FeedCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)
    class Meta:
        model = Feeds
        fields = ('__all__' )

class GroupCategoryFeedSerializer(serializers.ModelSerializer):
    intelgroup = IntelGroupSerializer(many=False, read_only=True)
    category = CategorySerializer(many=False, read_only=True)
    feed = FeedCategorySerializer(many=False, read_only=True)
    class Meta:
        model = GroupFeeds
        fields = ('__all__')

class FeedChannelSerializer(serializers.ModelSerializer):
    feed = GroupCategoryFeedSerializer(many=False, read_only=True)    
    class Meta:
        model = FeedChannels
        fields = ('__all__')

class APIkeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKeys
        fields = ('__all__')

class GroupWebHookSerializer(serializers.ModelSerializer):
    intelgroup = IntelGroupSerializer(many=False, read_only=True)
    class Meta:
        model = WebHooks
        fields = ('__all__' )

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
        fields = ('id', 'feeditem_id', 'isenable', 'globalindicator_id', 'value', 'feeditem', 'globalindicator')

class UserGlobalIndicatorSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(many=False, read_only=True)
    class Meta:
        model = GlobalIndicators
        fields = ('id', 'type', 'type_api', 'value', 'value_api', 'user')

class IndicatorGlobalSerializer(serializers.ModelSerializer):
    globalindicator = GlobalIndicatorSerializer(many=False, read_only=True)
    class Meta:
        model = Indicators
        fields = ('id', 'value', 'isenable', 'feeditem_id', 'globalindicator_id', 'globalindicator' )

class GlobalItemIndicatorSerializer(serializers.ModelSerializer):
    globalindicator = GlobalIndicatorSerializer(many=False, read_only=True)
    feeditem = FeedItemSerializer(many=False, read_only=True)
    class Meta:
        model = Indicators
        fields = ('id', 'value', 'isenable', 'feeditem_id', 'globalindicator_id', 'globalindicator', 'feeditem' )

class UserIndicatorWhitelistSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    globalindicator = GlobalIndicatorSerializer(many=False)
    class Meta:
        model = Whitelists
        fields = ('id', 'value', 'globalindicator_id', 'user_id', 'enabled', 'user', 'globalindicator')

class GroupGlobalAttributeSerializer(serializers.ModelSerializer):
    intelgroup = IntelGroupSerializer(many=False, read_only=True)
    globalattribute = GlobalAttributeSerializer(many=False, read_only=True)
    class Meta:
        model = GroupGlobalAttributes
        fields = ('__all__')

class UserGroupAttributeSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    intelgroup = IntelGroupSerializer(many=False, read_only=True)
    class Meta:
        model = Attributes
        fields = ('__all__')

class ItemReportSerializer(serializers.ModelSerializer):
    feeditem = FeedItemSerializer(many=False, read_only=True)
    class Meta:
        model = IntelReports
        fields = ('__all__')

class ChangeEmailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.CharField(max_length=100)

class IDSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class AccepInviteSerializer(serializers.Serializer):
    intelgroup_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)

class AttributeCreateSerializer(serializers.Serializer):
    attribute = serializers.CharField(max_length=100)
    value = serializers.CharField(max_length=100)
    words_matched = serializers.CharField(max_length=100)
    isenable = serializers.BooleanField()
    currentgroup = serializers.IntegerField()

class AttributeUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    attribute = serializers.CharField(max_length=100)
    value = serializers.CharField(max_length=100)
    words_matched = serializers.CharField(max_length=100)
    isenable = serializers.BooleanField()
    currentgroup = serializers.IntegerField()

class CategoryUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)

class CategoryCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)

class GroupIDSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    groupid = serializers.IntegerField()

class FeedCreateSerializer(serializers.Serializer):
    url = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=100)
    category = serializers.IntegerField()
    tags = serializers.IntegerField()
    confidence = serializers.IntegerField()
    intelgroup_id = serializers.IntegerField()

class FeedUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    url = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=100)
    manage_enabled = serializers.CharField(max_length=100)
    category = serializers.IntegerField()
    tags = serializers.IntegerField()
    confidence = serializers.IntegerField()

class EnabledSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    isenable = serializers.BooleanField()

class IntelgroupCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=100)
    userids = serializers.ListField(
        child = serializers.IntegerField()
    )
    emails = serializers.ListField(
        child = serializers.CharField(max_length=100)
    )

class IntelgroupUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=100)

class InviteSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    userids = serializers.ListField(
        child = serializers.IntegerField()
    )
    emails = serializers.ListField(
        child = serializers.CharField(max_length=100)
    )

class RoleUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    groupid = serializers.IntegerField()
    role = serializers.CharField(max_length=100)

class SearchFeedSerializer(serializers.Serializer):
    currentgroup = serializers.IntegerField()
    category = serializers.IntegerField()
    confidence = serializers.IntegerField()
    tags = serializers.CharField(max_length=100)

class SearchReportSerializer(serializers.Serializer):
    classification = serializers.IntegerField()
    category = serializers.IntegerField()
    tag = serializers.IntegerField()
    confidence = serializers.IntegerField()
    feedname = serializers.IntegerField()
    indicator = serializers.IntegerField()

class WebhookCreateSerializer(serializers.Serializer):
    intelgroup_id = serializers.IntegerField()
    endpoint = serializers.CharField(max_length=300)
    description = serializers.CharField(max_length=300)

class WebhookUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    intelgroup_id = serializers.IntegerField()
    endpoint = serializers.CharField(max_length=300)
    description = serializers.CharField(max_length=300)

class WhitelistCreateSerializer(serializers.Serializer):
    indicator = serializers.IntegerField()
    value = serializers.CharField(max_length=100)
    enabled = serializers.CharField(max_length=100)

class APIKeyCreateSerializer(serializers.Serializer):
    intelgroup_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)

class APIGroupSerializer(serializers.Serializer):
    UUID = serializers.CharField(max_length=100)
    Name = serializers.CharField(max_length=100)
    Description = serializers.CharField(max_length=1000)
    Role = serializers.IntegerField()

class APIFeedSerializer(serializers.Serializer):
    UUID = serializers.CharField(max_length=100)
    Type = serializers.CharField(max_length=100)
    Feed_name = serializers.CharField(max_length=100)
    Feed_description = serializers.CharField(max_length=1000)
    Feed_URL = serializers.CharField(max_length=1000)
    Intel_Group_UUID = serializers.CharField(max_length=100)
    Confidence = serializers.IntegerField()
    Category = serializers.CharField(max_length=100)
    Tags = serializers.CharField(max_length=100)
    Datetime_created = serializers.DateTimeField()
    Datetime_last_polled = serializers.DateTimeField()
    Dateteim_last_data = serializers.DateTimeField()
    RSS = serializers.DictField()

class APIReportSerializer(serializers.Serializer):
    UUID = serializers.UUIDField()
    Channel_UUID = serializers.UUIDField()
    Intel_Group_UUID = serializers.UUIDField()
    Report_URL = serializers.CharField(max_length=1000)
    Datetime_added = serializers.DateTimeField()
    RSS_data = serializers.DictField(
        child=serializers.CharField()
    )
    Indicators = serializers.DictField(
        child=serializers.DictField(
            child=serializers.CharField(max_length=100)
        ),
    )
    Attributes = serializers.DictField(
        child=serializers.ListField(
            child=serializers.DictField(
                child=serializers.CharField(max_length=100)
            )
        )
    )
