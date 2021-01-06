from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum, Count
from django.templatetags.static import static
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Extractions
from ..serializers import UserExtractionSerializer

class ExtractionViewSet(viewsets.ModelViewSet):

    queryset = Extractions.objects.order_by('id').all()
    serializer_class = UserExtractionSerializer

    def get_queryset(self):
        extractions = Extractions.objects.filter(user_id=self.request.user.id).order_by('id').all()
        return extractions

    def create(self, request):
        Extractions.objects.create(types=request.data['types'], value=request.data['value'], words_matched=request.data['words_matched'], enabled=request.data['enabled'], user_id=request.user.id);
        create_data = Extractions.objects.filter(user_id=request.user.id).last()
        serializer = UserExtractionSerializer(create_data)
        return Response(serializer.data)