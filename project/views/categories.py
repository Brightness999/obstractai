from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum, Count
from django.templatetags.static import static
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Categories
from ..serializers import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Categories.objects.order_by('id').all()
    serializer_class = CategorySerializer