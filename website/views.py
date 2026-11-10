from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from menu.models import Category, MenuItem
from orders.models import Order, OrderItem
from tables.models import Table
from reservations.models import Reservation


# ---------- Home ----------
def home(request):
    featured = MenuItem.objects.filter(is_available=True).order_by('-created_at')[:6]
    categories = Category.objects.all()[:6]
    return render(request, 'website/home.html', {
        'featured_items': featured,
        'categories': categories,
    })


# ---------- Menu ----------
def menu_list(request):
    categories = Category.objects.prefetch_related('items').all()
    return render(request, 'website/menu_list.html', {'categories': categories})


def menu_detail(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    related = MenuItem.objects.filter(
        category=item.category, is_available=True
    ).exclude(id=item.id)[:4]
    return render(request, 'website/menu_detail.html', {
        'item': item,
        'related_items': related,
    })


# ---------- Cart ----------
def _get_cart(request):
    return request.session.setdefault('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def cart_view(request):
    cart = _get_cart(request)
    items = []
    subtotal = Decimal('0.00')

    for item_id, qty in cart.items():
        try:
            menu_item = MenuItem.objects.get(id=int(item_id), is_available=True)
        except MenuItem.DoesNotExist:
            continue
        line_total = menu_item.price * qty
        subtotal += line_total
        items.append({
            'menu_item': menu_item,
            'quantity': qty,
            'line_total': line_total,
        })

    tax = (subtotal * Decimal('0.10')).quantize(Decimal('0.01'))
    total = subtotal + tax

    return render(request, 'website/cart.html', {
        'items': items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
    })


def cart_add(request, item_id):
    if request.method != 'POST':
        return redirect('website:menu_list')

    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    qty = int(request.POST.get('quantity', 1))
    if qty < 1:
        qty = 1

    cart = _get_cart(request)
    cart[str(item.id)] = cart.get(str(item.id), 0) + qty
    _save_cart(request, cart)

    messages.success(request, f'Added {item.name} to cart.')
    return redirect(request.POST.get('next') or 'website:cart')


def cart_update(request, item_id):
    if request.method != 'POST':
        return redirect('website:cart')

    cart = _get_cart(request)
    qty = int(request.POST.get('quantity', 1))
    if qty < 1:
        cart.pop(str(item_id), None)
    else:
        cart[str(item_id)] = qty
    _save_cart(request, cart)
    return redirect('website:cart')


def cart_remove(request, item_id):
    cart = _get_cart(request)
    cart.pop(str(item_id), None)
    _save_cart(request, cart)
    messages.info(request, 'Item removed from cart.')
    return redirect('website:cart')


# ---------- Checkout ----------
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('website:menu_list')

    # Rebuild the cart in case prices changed
    items = []
    subtotal = Decimal('0.00')
    for item_id, qty in cart.items():
        try:
            menu_item = MenuItem.objects.get(id=int(item_id), is_available=True)
        except MenuItem.DoesNotExist:
            continue
        line_total = menu_item.price * qty
        subtotal += line_total
        items.append({'menu_item': menu_item, 'quantity': qty, 'line_total': line_total})

    tax = (subtotal * Decimal('0.10')).quantize(Decimal('0.01'))
    total = subtotal + tax

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        order_type = request.POST.get('order_type', 'pickup')
        table_id = request.POST.get('table')
        notes = request.POST.get('notes', '').strip()

        if not customer_name or not customer_phone:
            messages.error(request, 'Name and phone number are required.')
            return render(request, 'website/checkout.html', {
                'items': items, 'subtotal': subtotal, 'tax': tax, 'total': total,
                'tables': Table.objects.all(),
                'form_data': request.POST,
            })

        table = None
        if order_type == 'dinein' and table_id:
            table = Table.objects.filter(id=table_id).first()

        with transaction.atomic():
            order = Order.objects.create(
                table=table,
                customer_name=customer_name,
                customer_phone=customer_phone,
                status='PENDING',
                total_amount=total,
                tax=tax,
                service_charge=Decimal('0.00'),
                discount=Decimal('0.00'),
                notes=notes,
                created_by=None,
            )
            for line in items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=line['menu_item'],
                    quantity=line['quantity'],
                    unit_price=line['menu_item'].price,
                )

        request.session['cart'] = {}
        request.session.modified = True
        return redirect('website:order_success', order_id=order.id)

    return render(request, 'website/checkout.html', {
        'items': items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
        'tables': Table.objects.all(),
    })


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'website/order_success.html', {'order': order})


# ---------- Reservation ----------
def reserve(request):
    if request.method == 'POST':
        name = request.POST.get('customer_name', '').strip()
        phone = request.POST.get('customer_phone', '').strip()
        email = request.POST.get('customer_email', '').strip()
        guests = request.POST.get('number_of_guests')
        date_str = request.POST.get('reservation_date')
        time_str = request.POST.get('reservation_time')
        requests_txt = request.POST.get('special_requests', '').strip()

        errors = []
        if not name:
            errors.append('Name is required.')
        if not phone:
            errors.append('Phone number is required.')
        if not guests or not guests.isdigit() or int(guests) < 1:
            errors.append('A valid party size is required.')
        if not date_str or not time_str:
            errors.append('Date and time are required.')

        if not errors:
            # Find a table that fits the party size and is free at that time
            from datetime import datetime
            try:
                dt = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            except ValueError:
                errors.append('Invalid date/time.')
                dt = None

            if dt:
                end_dt = dt + timezone.timedelta(hours=2)
                busy_table_ids = Reservation.objects.filter(
                    status__in=['PENDING', 'CONFIRMED', 'CHECKED_IN'],
                    reservation_time__lt=end_dt,
                    reservation_end_time__gt=dt,
                ).values_list('table_id', flat=True)

                table = Table.objects.filter(
                    capacity__gte=int(guests)
                ).exclude(id__in=busy_table_ids).order_by('capacity').first()

                if not table:
                    errors.append(
                        'Sorry, no table available for that date/time. '
                        'Please try a different time or call us.'
                    )
                else:
                    Reservation.objects.create(
                        table=table,
                        customer_name=name,
                        customer_phone=phone,
                        customer_email=email,
                        number_of_guests=int(guests),
                        reservation_time=dt,
                        reservation_end_time=end_dt,
                        status='PENDING',
                        special_requests=requests_txt,
                        created_by=None,
                    )
                    messages.success(
                        request,
                        'Reservation received! We will confirm it shortly by phone.'
                    )
                    return redirect('website:reserve')

        for e in errors:
            messages.error(request, e)

    return render(request, 'website/reserve.html', {'form_data': request.POST})


# ---------- Static pages ----------
def about(request):
    return render(request, 'website/about.html')


def contact(request):
    return render(request, 'website/contact.html')