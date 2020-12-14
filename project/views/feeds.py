from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

# Create your views here.

def Feeds(request):
    if request.user.is_authenticated:
        return render(request, 'project/feed_list.html')
    else:
        return render(request, 'web/landing_page.html')