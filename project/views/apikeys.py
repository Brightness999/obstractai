from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from ..models import APIKeys
from ..serializers import APIKeySerializer, GroupAPIkeySerializer

@method_decorator(login_required, name='dispatch')
class APIKeysViewSet(viewsets.ModelViewSet):
    serializer_class = GroupAPIkeySerializer
    queryset = APIKeys.objects.all()

    def create(self, request):
        

        return Response({'sdf'})
