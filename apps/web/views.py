from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from project.models import IntelGroups, UserIntelGroupRoles
from project.serializers import IntelGroupSerializer



def home(request):
    if request.user.is_authenticated:

        return render(request, 'project/index.html', context={
            'active_tab': 'dashboard',
        })

    else:
        return render(request, 'web/landing_page.html')

def grouplist(request):
    groups = IntelGroups.objects.filter(ispublic=True).order_by('id').all()
    return render(request, 'project/grouplist.html', {'groups':groups})


