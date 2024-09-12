from django.shortcuts import redirect, render, get_object_or_404
from .models import *

def store(request):
     products = Product.objects.all()
     context = {'products': products}
     return render(request, 'store/store.html', context)

def cart(request):
    order, created = Order.objects.get_or_create(customer=request.user, status='pending')
    context = {'order': order}
    return render(request, 'store/cart.html', context)

def checkout(request):
    order = get_object_or_404(Order, customer=request.user, status='pending')

    if request.method == 'POST':
        # Cuando el usuario confirma el pedido, se procesa
        order.status = 'processed'
        order.get_total_price()  # Calcular el total
        order.save()

        # Mostrar una página de agradecimiento o redirigir a una página de éxito
        return render(request, 'store/checkout_success.html', {'order': order})

    # Mostrar la vista de checkout para que el usuario confirme el pedido
    context = {'order': order}
    return render(request, 'store/checkout.html', context)

def add_to_cart(request, product_id):
    # 1. Obtener el producto que se está agregando al carrito
    product = get_object_or_404(Product, id=product_id)

    # 2. Obtener el pedido pendiente del usuario, o crear uno nuevo si no existe
    # Esto asegura que cada usuario tenga un único pedido "pendiente" (el carrito actual)
    order, created = Order.objects.get_or_create(customer=request.user, status='pending')

    # 3. Verificar si el producto ya está en el carrito (es decir, en el pedido pendiente)
    # Si ya existe el producto en el pedido, no lo volvemos a agregar, solo incrementamos la cantidad
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product, price=product.price)

    # 4. Si el producto ya estaba en el carrito, simplemente incrementamos la cantidad
    if not created:
        order_item.quantity += 1
        order_item.save()

    # 5. Después de agregar el producto al carrito, redirigimos al usuario de nuevo al carrito o a otra página
    return redirect('cart')
