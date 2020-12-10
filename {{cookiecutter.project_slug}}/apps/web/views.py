from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
{% if cookiecutter.use_teams == 'y' %}

from apps.teams.decorators import login_and_team_required, team_admin_required
from apps.teams.util import get_default_team
{% endif %}


def home(request):
    if request.user.is_authenticated:
{% if cookiecutter.use_teams == 'y' %}
        team = get_default_team(request)
        if team:
            return HttpResponseRedirect(reverse('web:team_home', args=[team.slug]))
        else:
            messages.info(request, _(
                'Teams are enabled but you have no teams. '
                'Create a team below to access the rest of the dashboard.'
            ))
            return HttpResponseRedirect(reverse('teams:manage_teams'))
{% else %}
        return render(request, 'web/app_home.html', context={
            'active_tab': 'dashboard',
        })
{% endif %}
    else:
        return render(request, 'web/landing_page.html')
{% if cookiecutter.use_teams == 'y' %}


@login_and_team_required
def team_home(request, team_slug):
    assert request.team.slug == team_slug
    return render(request, 'web/app_home.html', context={
        'team': request.team,
        'active_tab': 'dashboard',
    })


@team_admin_required
def team_admin_home(request, team_slug):
    assert request.team.slug == team_slug
    return render(request, 'web/team_admin.html', context={
        'active_tab': 'team-admin',
        'team': request.team,
    })
{% endif %}
