from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

# Create your views here.

def home(request):
    
    if request.user.is_authenticated:
        return render(request, 'project/index.html')
    else:
        return render(request, 'web/landing_page.html')

# from .feeds import *
from .intelgroups import *
