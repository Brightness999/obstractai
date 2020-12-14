from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _



def home(request):
    if request.user.is_authenticated:

        return render(request, 'web/app_home.html', context={
            'active_tab': 'dashboard',
        })

    else:
        return render(request, 'web/landing_page.html')

