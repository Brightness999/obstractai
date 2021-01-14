import urllib
import xmltodict
import pprint
import json
import os

from urllib.parse import urlencode
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
from django.core.mail import send_mail
from cyobstract import extract
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
load_dotenv()

from ..models import IntelGroups, UserIntelGroupRoles
from ..serializers import IntelGroupSerializer, UserIntelGroupRolesSerializer, RoleGroupSerializer,GroupPlanSerializer, CommentSerializer


@method_decorator(login_required, name='dispatch')
class IntelGroupViewSet(viewsets.ModelViewSet):
    queryset = IntelGroups.objects.all()
    serializer_class = CommentSerializer
    def get_queryset(self):
        
        groups = IntelGroups.objects.order_by('id').all()
        return groups
    

    @action(detail=False, methods=['POST'])
    def newgroup(self, request):
        message = Mail(
            from_email='kardzavaryan@gmail.com',
            to_emails=request.data['emails'],
            subject='Cyobstract',
            html_content='<strong>Please register in Cyobstract.</strong><p><a href="http://sherlock-staging.obstractai.com">sherlock-staging.obstractai.com</a></p>')
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
        except Exception as e:
            print(str(e))
        name = ''
        if(request.data['name'] == ''):
            name = 'Intel Group' + str(IntelGroups.objects.last().id+1)
        else:
            name = request.data['name']
        IntelGroups.objects.create(name=name, description=request.data['description'])
        new_group = IntelGroups.objects.filter(name=name).all().values()
        UserIntelGroupRoles.objects.create(intelgroup_id=new_group[0]['id'], user_id=request.user.id, role=2)
        for invite_id in request.data['userids']:
            if invite_id != request.user.id:
                UserIntelGroupRoles.objects.create(intelgroup_id=new_group[0]['id'], user_id=invite_id, role=0)
        new_role = UserIntelGroupRoles.objects.filter(intelgroup_id=new_group[0]['id'], user_id=request.user.id).all()
        serializer = RoleGroupSerializer(new_role[0])
        return Response(serializer.data)
    def partial_update(self, request, pk):
        IntelGroups.objects.filter(pk=pk).update(name=request.data['name'],description=request.data['description'])
        new_role = UserIntelGroupRoles.objects.filter(intelgroup_id=pk, user_id=request.user.id).all()
        serializer = RoleGroupSerializer(new_role[0])
        return Response(serializer.data)

@method_decorator(login_required, name='dispatch')
class FullTextViewSet(viewsets.ModelViewSet):
    queryset = IntelGroups.objects.all()
    serializer_class = CommentSerializer

    @action(detail=False, methods=['GET'])
    def fulltext(self, request):
        ftr = "http://ftr-premium.fivefilters.org/"
        # encode = urllib.parse.quote_plus("http://feeds.bbci.co.uk/news/rss.xml")
        encode = urllib.parse.quote_plus("https://apnews.com/apf-topnews")
        req = urllib.request.Request(ftr+"makefulltextfeed.php?url="+encode+"&key=KSF8GH22GZRKA8")
        contents = urllib.request.urlopen(req).read()
        text = json.dumps(xmltodict.parse(contents)['rss']['channel']['item'])
        results = extract.extract_observables(text)
        print(type(xmltodict.parse(contents)['rss']['channel']['item']) is list)
        if type(xmltodict.parse(contents)['rss']['channel']['item']) is list:
            print(len(xmltodict.parse(contents)['rss']['channel']['item']))
            for items in xmltodict.parse(contents)['rss']['channel']['item']:
                for item in items:
                    print(items['title'])

        return Response(xmltodict.parse(contents))

class RoleIntelGroupViewSet(viewsets.ModelViewSet):
    queryset = IntelGroups.objects.all()
    serializer_class = RoleGroupSerializer

    def get_queryset(self):
        groups = UserIntelGroupRoles.objects.order_by('id').filter(user_id=self.request.user.id).all()
        return groups
    
    @action(detail=False, methods=['POST'])
    def invitate(self, request):
        UserIntelGroupRoles.objects.filter(id=request.data['role']).update(role = '1')
        groups = UserIntelGroupRoles.objects.order_by('id').filter(user_id=self.request.user.id).all()
        result = []
        for group in groups:
            serializer = RoleGroupSerializer(group)
            result.append(serializer.data)

        return Response(result)

    @action(detail=False, methods=['POST'])
    def reject(self, request):
        UserIntelGroupRoles.objects.filter(id=request.data['role']).delete()
        groups = UserIntelGroupRoles.objects.order_by('id').filter(user_id=self.request.user.id).all()
        result = []
        for group in groups:
            serializer = RoleGroupSerializer(group)
            result.append(serializer.data)

        return Response(result)
    
    @action(detail=False, methods=['POST'])
    def leave(self, request):
        result = []
        role = UserIntelGroupRoles.objects.filter(id=request.data['role']).all()
        if role[0].role == 1:
            UserIntelGroupRoles.objects.filter(id=request.data['role']).delete()
            groups = UserIntelGroupRoles.objects.order_by('id').filter(user_id=self.request.user.id).all()
            for group in groups:
                serializer = RoleGroupSerializer(group)
                result.append(serializer.data)
        elif role[0].role == 2:
            intelgroup_id = UserIntelGroupRoles.objects.filter(id=request.data['role']).all()[0].intelgroup_id
            users = UserIntelGroupRoles.objects.filter(intelgroup_id=intelgroup_id, role=2).all()
            if(len(users)<2):
                result.append({'message':True})
            else:
                UserIntelGroupRoles.objects.filter(id=request.data['role']).delete()
                groups = UserIntelGroupRoles.objects.order_by('id').filter(user_id=self.request.user.id).all()
                for group in groups:
                    serializer = RoleGroupSerializer(group)
                    result.append(serializer.data)

        return Response(result)
    
    @action(detail=False, methods=['POST'])
    def deleteIntelGroup(self, request):
        IntelGroups.objects.filter(id = request.data['role']).delete()
        return Response('Success')


class IntelGroupRoleViewSet(viewsets.ModelViewSet):
    serializer_class = UserIntelGroupRolesSerializer
    queryset = UserIntelGroupRoles.objects.all()

    @action(detail=False, methods=['POST'])
    def makeadmin(self, request):
        target_user = UserIntelGroupRoles.objects.filter(id=request.data['role'])
        if(target_user[0].role == 1):
            target_user.update(role=2)
        elif(target_user[0].role == 2):
            target_user.update(role=1)
        user_role = UserIntelGroupRoles.objects.all().filter(intelgroup_id=target_user[0].intelgroup_id).filter(user_id=request.user.id).values('role')
        users = UserIntelGroupRoles.objects.filter(intelgroup_id=target_user[0].intelgroup_id).select_related('user').all()
        data = []
        for user in users:
            serializer = UserIntelGroupRolesSerializer(user)
            data.append(serializer.data)
        result = []
        result.append(user_role[0]['role'])
        result.append(request.user.id)
        result.append(data)
        return Response(result)

