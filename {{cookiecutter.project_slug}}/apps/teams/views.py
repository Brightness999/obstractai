from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from rest_framework import viewsets

from apps.teams.decorators import login_and_team_required, team_admin_required
from .invitations import send_invitation, process_invitation, clear_invite_from_session
from .forms import TeamChangeForm
from .models import Team, Invitation
from .serializers import TeamSerializer, InvitationSerializer


@login_required
def manage_teams(request):
    return render(request, 'teams/teams.html', {})


@login_required
def list_teams(request):
    teams = request.user.teams.all()
    return render(request, 'teams/list_teams.html', {
        'teams': teams,
    })


@login_required
def create_team(request):
    if request.method == 'POST':
        form = TeamChangeForm(request.POST)
        if form.is_valid():
            team = form.save()
            team.members.add(request.user, through_defaults={'role': 'admin'})
            team.save()
            return HttpResponseRedirect(reverse('teams:list_teams'))
    else:
        form = TeamChangeForm()
    return render(request, 'teams/manage_team.html', {
        'form': form,
        'create': True,
    })


@login_and_team_required
def manage_team(request, team_slug):
    team = request.team
    if request.method == 'POST':
        form = TeamChangeForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('teams:list_teams'))
    else:
        form = TeamChangeForm(instance=team)
    return render(request, 'teams/manage_team.html', {
        'team': team,
        'form': form,
    })


def accept_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id)
    if not invitation.is_accepted:
        # set invitation in the session in case needed later
        request.session['invitation_id'] = invitation_id
    else:
        clear_invite_from_session(request)
    return render(request, 'teams/accept_invite.html', {
        'invitation': invitation,
    })


@login_required
@require_POST
def accept_invitation_confirm(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id)
    if invitation.is_accepted:
        messages.error(request, _('Sorry, it looks like that invitation link has expired.'))
        return HttpResponseRedirect(reverse('web:home'))
    else:
        process_invitation(invitation, request.user)
        clear_invite_from_session(request)
        messages.success(request, _('You successfully joined {}').format(invitation.team.name))
        return HttpResponseRedirect(reverse('web:team_home', args=[invitation.team.slug]))


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_queryset(self):
        # filter queryset based on logged in user
        return self.request.user.teams.all()

    def perform_create(self, serializer):
        # ensure logged in user is set on the model during creation
        team = serializer.save()
        team.members.add(self.request.user, through_defaults={'role': 'admin'})


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer

    def get_queryset(self):
        # filter queryset based on logged in user
        return self.queryset.filter(team__in=self.request.user.teams.all())

    def perform_create(self, serializer):
        # ensure logged in user is set on the model during creation
        invitation = serializer.save(invited_by=self.request.user)
        send_invitation(invitation)


@team_admin_required
def resend_invitation(request, team, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id)
    if invitation.team != request.team:
        raise ValueError(_('Request team {team} did not match invitation team {invite_team}').format(
            team=request.team.slug,
            invite_team=invitation.team.slug,
        ))
    send_invitation(invitation)
    return HttpResponse('Ok')
