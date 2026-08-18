
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer, MenuItemCreateSerializer
from inventory.models import Ingredient

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MenuItemCreateSerializer
        return MenuItemSerializer

    @action(detail=True, methods=['post'])
    def update_availability(self, request, pk=None):
        menu_item = self.get_object()
        is_available = request.data.get('is_available')
        if is_available is not None:
            menu_item.is_available = is_available
            menu_item.save()
            return Response({'status': 'Availability updated'})
        return Response({'error': 'is_available field required'}, status=status.HTTP_400_BAD_REQUEST)