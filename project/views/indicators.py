from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum, Count
from django.templatetags.static import static
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import GlobalIndicators
from ..serializers import UserGlobalIndicatorSerializer

class IndicatorViewSet(viewsets.ModelViewSet):
    
    queryset = GlobalIndicators.objects.order_by('id').all()
    serializer_class = UserGlobalIndicatorSerializer

    def create(self, request):
        GlobalIndicators.objects.create(type=request.data['type'], type_api=request.data['type_api'], value=request.data['value'], value_api=request.data['value_api'], user_id=request.user.id, enabled=request.data['enabled'])
        create_data = GlobalIndicators.objects.last()
        serializer = UserGlobalIndicatorSerializer(create_data)
        return Response(serializer.data)