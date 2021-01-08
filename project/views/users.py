from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from rest_framework.decorators import action
import json


from apps.users.models import CustomUser
from ..serializers import UserIntelGroupRolesSerializer, CustomUserSerializer, UsersInvitationSerializer
from ..models import UserIntelGroupRoles


@method_decorator(login_required, name='dispatch')
class UserViewSet(viewsets.ModelViewSet):

	queryset = CustomUser.objects.all()
	serializer_class = UserIntelGroupRolesSerializer

	def get_queryset(self):
		print(self.request)
		admin_group_id = UserIntelGroupRoles.objects.all().filter(user_id=self.request.user.id).filter(role=2)[0].intelgroup_id
		users = UserIntelGroupRoles.objects.filter(intelgroup_id=admin_group_id).select_related('user').all()

		return users
	@action(detail=False, methods=['POST'])
	def manage(self,request):
		print(request.data)
		# if(request.data['role'] == 'new'):
		# 	return Response([])
		user_role = UserIntelGroupRoles.objects.all().filter(intelgroup_id=request.data['role']).filter(user_id=request.user.id).values('role')
		users = UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['role']).select_related('user').all()
		data = []
		for user in users:
			serializer = UserIntelGroupRolesSerializer(user)
			data.append(serializer.data)
		result = []
		result.append(user_role[0]['role'])
		result.append(request.user.id)
		result.append(data)

		return Response(result)
@method_decorator(login_required, name='dispatch')
class UserInvitationViewSet(viewsets.ModelViewSet):
    	
	queryset = CustomUser.objects.all()
	serializer_class = UsersInvitationSerializer

	@action(detail=False, methods=['POST'])
	def invitation(self, request):
		data = [];
		for userid in request.data['userids']:
			existing_user = UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['group_id'], user_id=userid).all()
			if len(existing_user) == 0:
				UserIntelGroupRoles.objects.create(intelgroup_id=request.data['group_id'], user_id=userid, role=0)
				user = UserIntelGroupRoles.objects.filter(intelgroup_id=request.data['group_id'], user_id=userid, role=0).all()
				serializer = UserIntelGroupRolesSerializer(user[0])
				data.append(serializer.data)
		if(len(data) == 0):
    			data=[{'role': 'success'}]
		return Response(data)
			


	
