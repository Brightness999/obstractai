from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

from ..models.intelgroups import IntelGroups
from ..serializers import IntelGroupSerializer

# Create your views here.

@method_decorator(login_required, name='dispatch')
class ObjectLifecycleView(TemplateView):
    def get_context_data(self, **kwargs):
        return {
            'department_choices': [{
                'id': c[0],
                'name': c[1]
            } for c in Employee.DEPARTMENT_CHOICES],
        }


class ReactObjectLifecycleView(ObjectLifecycleView):
    template_name = 'project/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'framework_url': 'https://reactjs.org/',
            'framework_name': 'React',
            'framework_icon': static('images/pegasus/react-icon.png'),
            'active_tab': 'react_object_lifecycle',
        })
        return context

class IntelGroupViewSet(viewsets.ModelViewSet):
    queryset = IntelGroups.objects.all()
    serializer_class = IntelGroupSerializer

    # def get_queryset(self):
    #     # filter queryset based on logged in user
    #     return self.request.user.intelgroups.all()

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
# def IntelGroup(request):
#     if request.user.is_authenticated:
#         if(request.method == 'GET'):
#             print(request.method)
#             data = IntelGroups.objects.all()
#             return data
#     else:
#         return render(request, 'web/landing_page.html')