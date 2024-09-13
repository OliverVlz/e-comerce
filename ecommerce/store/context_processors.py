from .models import Order

def cart_items_count(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(customer=request.user, status='pending').first()
        count = order.items.count() if order else 0
    else:
        count = 0
    return {'cart_items_count': count}
