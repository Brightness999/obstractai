from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

# Create your views here.

@method_decorator(login_required, name='dispatch')
class ObjectLifecycleView(TemplateView):
    def get_context_data(self, **kwargs):
        return {
            
            } 
        
class Home(ObjectLifecycleView):
    template_name = 'project/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'framework_url': 'https://reactjs.org/',
            'framework_name': 'React',
            'active_tab': 'react_object_lifecycle',
        })
        return context

# from .feeds import *
from .intelgroups import *
from .users import *
from .customers import *
from .feeds import *
from .categories import *
from .tags import *
from .extractions import *
from .globalindicators import *
from .whitelist import *
from .apikeys import *