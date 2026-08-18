
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from inventory.models import InventoryTransaction
from menu.models import MenuItemIngredient

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return OrderCreateSerializer
        return OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check table availability
        table = serializer.validated_data.get('table')
        if table and table.status == 'OCCUPIED':
            return Response(
                {'error': 'Table is already occupied'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check ingredient availability
        items_data = serializer.validated_data.get('items', [])
        insufficient_stock = []
        
        for item_data in items_data:
            menu_item = item_data['menu_item']
            quantity = item_data['quantity']
            
            # Check if menu item has ingredients
            ingredient_items = MenuItemIngredient.objects.filter(menu_item=menu_item)
            
            if ingredient_items.exists():
                for ingredient_item in ingredient_items:
                    ingredient = ingredient_item.ingredient
                    required_quantity = ingredient_item.quantity_required * quantity
                    
                    if ingredient.quantity < required_quantity:
                        insufficient_stock.append({
                            'ingredient': ingredient.name,
                            'required': float(required_quantity),
                            'available': float(ingredient.quantity),
                            'menu_item': menu_item.name
                        })
        
        if insufficient_stock:
            return Response(
                {
                    'error': 'Insufficient stock for ingredients',
                    'details': insufficient_stock
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create order
        order = serializer.save()
        
        # Update inventory
        for item_data in items_data:
            menu_item = item_data['menu_item']
            quantity = item_data['quantity']
            
            ingredient_items = MenuItemIngredient.objects.filter(menu_item=menu_item)
            
            for ingredient_item in ingredient_items:
                ingredient = ingredient_item.ingredient
                used_quantity = ingredient_item.quantity_required * quantity
                
                # Update ingredient quantity
                ingredient.quantity -= used_quantity
                ingredient.save()
                
                # Create inventory transaction
                InventoryTransaction.objects.create(
                    ingredient=ingredient,
                    transaction_type='OUT',
                    quantity=used_quantity,
                    unit_price=ingredient.unit_price,
                    notes=f"Used for order #{order.id} - {menu_item.name}",
                    created_by=str(request.user) if request.user else 'System'
                )
        
        # Update table status
        if table:
            table.status = 'OCCUPIED'
            table.save()
        
        # Calculate total
        order.calculate_total()
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': f'Invalid status. Choose from: {dict(Order.STATUS_CHOICES).keys()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If order is completed or cancelled, free the table
        if new_status in ['COMPLETED', 'CANCELLED'] and order.table:
            order.table.status = 'AVAILABLE'
            order.table.save()
        
        order.status = new_status
        order.save()
        
        return Response({
            'status': 'Order status updated',
            'order_id': order.id,
            'new_status': order.status
        })

    @action(detail=False, methods=['get'])
    def today_orders(self, request):
        """Get today's orders"""
        from django.utils import timezone
        today = timezone.now().date()
        orders = self.queryset.filter(created_at__date=today)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)