
from rest_framework import serializers
from .models import Order, OrderItem
from menu.models import MenuItem
from tables.models import Table

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'unit_price', 
                 'special_instructions', 'subtotal']

class OrderItemCreateSerializer(serializers.Serializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    quantity = serializers.IntegerField(min_value=1)
    special_instructions = serializers.CharField(required=False, allow_blank=True)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    table_number = serializers.CharField(source='table.table_number', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'table', 'table_number', 'customer_name', 'customer_phone', 
                 'status', 'total_amount', 'tax', 'discount', 'service_charge', 
                 'notes', 'created_by', 'created_by_name', 'items', 'created_at', 'updated_at']

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = Order
        fields = ['table', 'customer_name', 'customer_phone', 'items', 
                 'tax', 'discount', 'service_charge', 'notes']
    
    def validate(self, data):
        # Validate table availability
        table = data.get('table')
        if table and table.status == 'OCCUPIED':
            raise serializers.ValidationError("Table is already occupied")
        return data
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            menu_item = item_data['menu_item']
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=item_data['quantity'],
                unit_price=menu_item.price,
                special_instructions=item_data.get('special_instructions', '')
            )
        
        return order