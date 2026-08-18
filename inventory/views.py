
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F, Q
from .models import Ingredient, InventoryTransaction
from .serializers import IngredientSerializer, InventoryTransactionSerializer

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get all ingredients that are below or at reorder level"""
        low_stock_items = Ingredient.objects.filter(quantity__lte=F('reorder_level'))
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get all ingredients that are out of stock"""
        out_of_stock_items = Ingredient.objects.filter(quantity=0)
        serializer = self.get_serializer(out_of_stock_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def restock(self, request, pk=None):
        ingredient = self.get_object()
        quantity = request.data.get('quantity')
        unit_price = request.data.get('unit_price')
        notes = request.data.get('notes', 'Restock')
        
        if not quantity:
            return Response(
                {'error': 'Quantity is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = float(quantity)
            if quantity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': 'Quantity must be a positive number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update ingredient quantity
        ingredient.quantity += quantity
        ingredient.save()
        
        # Create inventory transaction
        InventoryTransaction.objects.create(
            ingredient=ingredient,
            transaction_type='IN',
            quantity=quantity,
            unit_price=unit_price or ingredient.unit_price,
            notes=notes,
            created_by=str(request.user) if request.user else 'System'
        )
        
        return Response({
            'status': 'Restock successful',
            'ingredient': IngredientSerializer(ingredient).data,
            'transaction': {
                'quantity': quantity,
                'unit_price': unit_price or ingredient.unit_price,
                'notes': notes
            }
        })

class InventoryTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryTransaction.objects.all().order_by('-created_at')
    serializer_class = InventoryTransactionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        ingredient_id = self.request.query_params.get('ingredient')
        transaction_type = self.request.query_params.get('type')
        
        if ingredient_id:
            queryset = queryset.filter(ingredient_id=ingredient_id)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        return queryset