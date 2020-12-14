from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .util import get_next_unique_team_slug
from .models import Team, Membership, Invitation



class MembershipSerializer(serializers.ModelSerializer):
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    display_name = serializers.ReadOnlyField(source='user.get_display_name')

    class Meta:
        model = Membership
        fields = ('id', 'first_name', 'last_name', 'display_name', 'role')


class InvitationSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    invited_by = serializers.ReadOnlyField(source='invited_by.get_display_name')

    class Meta:
        model = Invitation
        fields = ('id', 'team', 'email', 'role', 'invited_by', 'is_accepted')


class TeamSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        required=False,
        validators=[UniqueValidator(queryset=Team.objects.all())],
    )
    members = MembershipSerializer(source='sorted_memberships', many=True, read_only=True)
    invitations = InvitationSerializer(many=True, read_only=True, source='pending_invitations')
    dashboard_url = serializers.ReadOnlyField()

    class Meta:
        model = Team
        fields = ('id', 'name', 'slug', 'members', 'invitations', 'dashboard_url')

    def create(self, validated_data):
        team_name = validated_data.get("name", None)
        validated_data['slug'] = validated_data.get("slug", get_next_unique_team_slug(team_name))
        return super().create(validated_data)
