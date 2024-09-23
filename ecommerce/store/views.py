from django.shortcuts import redirect, render, get_object_or_404
from .models import *
from .forms import UserSignupForm, UserLoginForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def store(request):
    products = Product.objects.all()

    # Obtener el carrito del usuario actual
    if request.user.is_authenticated:
        order = Order.objects.filter(customer=request.user, status='pending').first()
        cart_items_count = order.items.count() if order else 0
    else:
        cart_items_count = 0

    context = {
        'products': products,
        'cart_items_count': cart_items_count,  # Contador de productos únicos en el carrito
    }
    return render(request, 'store/store.html', context)

def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('store')  
    else:
        form = UserSignupForm()
    return render(request, 'store/signup.html', {'form': form})

class CustomLoginView(LoginView):
    form_class = UserLoginForm  
    template_name = 'store/login.html'  

@login_required
def profile(request):
    return render(request, 'store/profile.html')

def logout_view(request):
    logout(request)
    return redirect('store')

@login_required
def cart(request):
    order, created = Order.objects.get_or_create(customer=request.user, status='pending')
    context = {'order': order}
    return render(request, 'store/cart.html', context)

@login_required
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

@login_required
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

@login_required
def remove_from_cart(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id)
    order_item.delete()  # Elimina el producto completamente
    return redirect('cart')

@login_required
def decrease_quantity(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id)
    
    # Si la cantidad es mayor que 1, disminuye la cantidad
    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        # Si la cantidad es 1, eliminamos el item
        order_item.delete()
    
    return redirect('cart')
