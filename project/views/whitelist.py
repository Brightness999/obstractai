from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum, Count
from django.templatetags.static import static
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Whitelists
from ..serializers import UserIndicatorWhitelistSerializer

class WhitelistViewSet(viewsets.ModelViewSet):
    
    queryset = Whitelists.objects.order_by('id').all()
    serializer_class = UserIndicatorWhitelistSerializer

    def create(self, request):
        print(request.data)
        Whitelists.objects.create(indicator_id=request.data['indicator'],value=request.data['value'], user_id=request.user.id, enabled=request.data['enabled'] )
        create_data = Whitelists.objects.last()
        serializer = UserIndicatorWhitelistSerializer(create_data)
        return Response(serializer.data)