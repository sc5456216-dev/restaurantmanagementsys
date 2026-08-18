
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q, Avg, F  
from django.utils import timezone
from datetime import datetime, timedelta
from collections import Counter
import json

from orders.models import Order, OrderItem
from inventory.models import Ingredient

class ReportViewSet(viewsets.GenericViewSet):
    
    @action(detail=False, methods=['get'])
    def daily_sales(self, request):
        """Get daily sales report"""
        date_str = request.query_params.get('date')
        
        try:
            if date_str:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                date_obj = timezone.now().date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get orders for the day
        orders = Order.objects.filter(
            created_at__date=date_obj,
            status__in=['COMPLETED', 'SERVED']
        )
        
        total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_orders = orders.count()
        
        # Get popular items
        popular_items = []
        for order in orders:
            for item in order.items.all():
                popular_items.append(item.menu_item.name)
        
        popular_items_count = Counter(popular_items).most_common(5)
        
        # Get table utilization
        tables_used = orders.filter(table__isnull=False).values('table__table_number').distinct().count()
        
        return Response({
            'date': date_obj,
            'total_sales': float(total_sales),
            'total_orders': total_orders,
            'average_order_value': float(total_sales / total_orders) if total_orders > 0 else 0,
            'tables_used': tables_used,
            'popular_items': [
                {'name': name, 'count': count} 
                for name, count in popular_items_count
            ]
        })

    @action(detail=False, methods=['get'])
    def stock_alerts(self, request):
        """Get stock alerts for low inventory"""
        # Fixed: Added F() import
        low_stock = Ingredient.objects.filter(
            quantity__lte=F('reorder_level'),
            quantity__gt=0
        )
        out_of_stock = Ingredient.objects.filter(quantity=0)
        
        return Response({
            'low_stock': [
                {
                    'id': ing.id,
                    'name': ing.name,
                    'quantity': float(ing.quantity),
                    'reorder_level': float(ing.reorder_level),
                    'unit': ing.unit
                } 
                for ing in low_stock
            ],
            'out_of_stock': [
                {
                    'id': ing.id,
                    'name': ing.name,
                    'quantity': float(ing.quantity),
                    'unit': ing.unit
                } 
                for ing in out_of_stock
            ],
            'total_alerts': low_stock.count() + out_of_stock.count()
        })

    @action(detail=False, methods=['get'])
    def revenue_report(self, request):
        """Get revenue report for a period"""
        days = int(request.query_params.get('days', 30))
        
        if days < 1 or days > 365:
            return Response(
                {'error': 'Days must be between 1 and 365'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        orders = Order.objects.filter(
            created_at__range=[start_date, end_date],
            status__in=['COMPLETED', 'SERVED']
        )
        
        # Daily revenue
        daily_revenue = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            day_orders = orders.filter(created_at__date=day.date())
            total = day_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            daily_revenue.append({
                'date': day.date(),
                'revenue': float(total),
                'orders': day_orders.count()
            })
        
        # Weekly summary
        weekly_revenue = []
        for i in range(0, days, 7):
            week_start = start_date + timedelta(days=i)
            week_end = min(week_start + timedelta(days=7), end_date)
            week_orders = orders.filter(
                created_at__date__gte=week_start.date(),
                created_at__date__lt=week_end.date()
            )
            total = week_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            weekly_revenue.append({
                'week_start': week_start.date(),
                'week_end': week_end.date(),
                'revenue': float(total),
                'orders': week_orders.count()
            })
        
        total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        return Response({
            'period': f'{days} days',
            'start_date': start_date.date(),
            'end_date': end_date.date(),
            'total_revenue': float(total_revenue),
            'total_orders': orders.count(),
            'average_daily_revenue': float(total_revenue / days) if days > 0 else 0,
            'daily_revenue': daily_revenue,
            'weekly_summary': weekly_revenue
        })

    @action(detail=False, methods=['get'])
    def menu_performance(self, request):
        """Get menu item performance report"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        order_items = OrderItem.objects.filter(
            order__created_at__gte=start_date,
            order__status__in=['COMPLETED', 'SERVED']
        )
        
        # Performance by menu item
        menu_performance = []
        menu_items = order_items.values('menu_item__id', 'menu_item__name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('unit_price'),
            avg_price=Avg('unit_price'),
            order_count=Count('order', distinct=True)
        ).order_by('-total_revenue')
        
        total_revenue = sum(item['total_revenue'] or 0 for item in menu_items)
        
        for item in menu_items:
            revenue = float(item['total_revenue'] or 0)
            menu_performance.append({
                'menu_item_id': item['menu_item__id'],
                'name': item['menu_item__name'],
                'quantity_sold': item['total_quantity'] or 0,
                'revenue': revenue,
                'percentage_of_total': (revenue / total_revenue * 100) if total_revenue > 0 else 0,
                'average_price': float(item['avg_price'] or 0),
                'order_count': item['order_count']
            })
        
        return Response({
            'period': f'{days} days',
            'total_menu_revenue': float(total_revenue),
            'total_items_sold': sum(item['quantity_sold'] for item in menu_performance),
            'menu_performance': menu_performance
        })