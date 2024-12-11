from django.shortcuts import redirect, render, get_object_or_404
from .models import *
from .forms import UserSignupForm, UserLoginForm, ProductForm, UserProfileForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse
from django.utils.safestring import mark_safe

import random

def store(request):
    products = Product.objects.filter(is_active=True)

    # Generar un diccionario de productos destacados con featured_order como clave
    featured_products_dict = {
        f"featured_product_{i}": products.filter(is_featured=True, featured_order=i).first()
        for i in range(1, 9)
    }

    # Obtener todos los productos destacados y productos normales
    featured_products = products.filter(is_featured=True).order_by('featured_order')[:8]
    normal_products = products.exclude(id__in=featured_products)

    # Obtener el carrito del usuario actual
    if request.user.is_authenticated:
        order = Order.objects.filter(customer=request.user, status='pending').first()
        cart_items_count = order.items.count() if order else 0
    else:
        cart_items_count = 0

    # Agregar los productos destacados al contexto
    context = {
        **featured_products_dict,  # Unpack del diccionario de productos destacados
        'featured_products': featured_products,  # Otros productos destacados
        'products': normal_products,  # Productos no destacados
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
            print(form.errors)
    else:
        form = UserSignupForm()
    return render(request, 'store/signup.html', {'form': form})

class CustomLoginView(LoginView):
    form_class = UserLoginForm  
    template_name = 'store/login.html'  

@login_required
def user_profile(request):
    # Lógica para distinguir entre tipos de usuarios
    if request.user.user_type == 2:
        # Es un distribuidor
        return redirect('distributor_profile')
    else:
        # Es un cliente o administrador
        return render(request, 'store/user-profile.html', {'user': request.user})

@login_required
def distributor_profile(request):
    if request.user.user_type != 2:
        # Redirige si no es distribuidor
        return redirect('profile')
    return render(request, 'store/distributor-profile.html', {'user': request.user})

@login_required
def logout_view(request):
    logout(request)
    return redirect('store')

@login_required
def cart(request):
    order, created = Order.objects.get_or_create(customer=request.user, status='pending')
    context = {'order': order}
    return render(request, 'store/cart.html', context)

@login_required
def cart_view(request):
    order, created = Order.objects.get_or_create(customer=request.user, status='pending')
    unavailable_items = [item for item in order.items.all() if not item.product.is_active]

    if unavailable_items:
        messages.info(
            request, 
            "Algunos productos de tu carrito no están disponibles. Por favor, elimínalos para continuar con la compra."
        )

    context = {
        'order': order,
        'unavailable_items': unavailable_items,
        'total_price': order.get_total_price()  # Usar el cálculo actualizado
    }
    return render(request, 'store/cart.html', context)

@login_required
def remove_unavailable_items(request):
    # Obtener el pedido "pendiente" del usuario
    order = Order.objects.filter(customer=request.user, status='pending').first()

    if order:
        # Eliminar productos no disponibles
        order.items.filter(product__is_active=False).delete()

    # Redirigir al checkout
    return redirect('checkout')

@login_required
def checkout(request):
    order = get_object_or_404(Order, customer=request.user, status='pending')

    # Verificar si hay productos no disponibles
    unavailable_items = [item for item in order.items.all() if not item.product.is_active]

    if unavailable_items:
        # Construir la URL para eliminar elementos no disponibles
        remove_items_url = reverse('remove_unavailable_items')
        
        # Mostrar mensaje de advertencia con un botón
        messages.warning(
            request, 
            mark_safe(  # Permitir HTML en el mensaje
                f"No puedes proceder al checkout porque hay productos no disponibles en tu carrito. "
                f"Por favor, <a href='{remove_items_url}' class='btn btn-sm btn-danger'>elimina y continúa</a>."
            )
        )
        return redirect('cart')

    if request.method == 'POST':
        # Confirmar pedido
        order.status = 'processed'
        order.get_total_price()
        order.save()
        return render(request, 'store/checkout_success.html', {'order': order})

    context = {'order': order}
    return render(request, 'store/checkout.html', context)

@login_required
def buy_now(request, product_id):
    # Obtener el producto que se está comprando
    product = get_object_or_404(Product, id=product_id)

    # Obtener la cantidad de la solicitud, con valor predeterminado de 1
    quantity = int(request.GET.get('quantity', 1))

    # Obtener o crear el pedido pendiente (carrito) del usuario
    order, created = Order.objects.get_or_create(customer=request.user, status='pending')

    # Agregar el producto al carrito o incrementar la cantidad si ya existe
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product, price=product.price)
    if not created:
        order_item.quantity += quantity
    else:
        order_item.quantity = quantity
    order_item.save()

    # Redirigir al checkout para completar la compra
    return redirect('checkout')

@login_required
def add_to_cart(request, product_id):
    # Obtener el producto que se está agregando al carrito
    product = get_object_or_404(Product, id=product_id)

    # Obtener la cantidad de la solicitud, con valor predeterminado de 1
    quantity = int(request.GET.get('quantity', 1))

    # Obtener el pedido pendiente del usuario, o crear uno nuevo si no existe
    order, created = Order.objects.get_or_create(customer=request.user, status='pending')

    # Verificar si el producto ya está en el carrito
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product, price=product.price)

    # Ajustar la cantidad del OrderItem
    if not created:
        order_item.quantity += quantity
    else:
        order_item.quantity = quantity
    order_item.save()

    # Redirigir al carrito
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id)
    order_item.delete()  # Elimina el producto completamente
    return redirect('cart')

@login_required
def remove_from_checkout(request, item_id):
    # Obtener el item del pedido
    item = get_object_or_404(OrderItem, id=item_id, order__customer=request.user, order__status='pending')
    item.delete()
    return redirect('checkout')

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

def add_product(request):
    if request.user.user_type != 2:  # Verificar que el usuario sea distribuidor
        return redirect('store')  # Redirigir si no es distribuidor

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.distributor = request.user.distributor_profile
            product.save()
            return redirect('distributor-products')  # Verifica que el nombre de la URL sea correcto
    else:
        form = ProductForm()
    return render(request, 'store/add-product.html', {'form': form})  # Verifica que el nombre de la plantilla sea correcto

def distributor_products(request):
    if request.user.user_type != 2:  # Verificar que el usuario sea distribuidor
        return redirect('store')  # Redirigir si no es distribuidor

    products = Product.objects.filter(distributor=request.user.distributor_profile)
    return render(request, 'store/distributor-products.html', {'products': products})

def products(request):
    products = Product.objects.all()  # Obtener todos los productos

    context = {
        'products': products,  # Pasar los productos al contexto
    }
    return render(request, 'store/products.html', context)

def products_view(request):
    categories = Category.objects.filter(parent__isnull=True)
    
    category_data = []
    for category in categories:
        subcategories = category.subcategories.all()
        category_data.append({
            'category': category,
            'subcategories': [
                {
                    'subcategory': subcategory,
                    'products': Product.objects.filter(category=subcategory, is_active=True)  # Solo productos activos
                }
                for subcategory in subcategories
            ]
        })
    
    print(category_data)  # Imprime los datos en la consola para verificar
    
    context = {
        'category_data': category_data,
    }
    
    return render(request, 'store/products.html', context)

def products_list(request, subcategory_slug):
    # Obtener la subcategoría basada en el slug
    subcategory = get_object_or_404(Category, slug=subcategory_slug)
    
    # Obtener todos los productos de esa subcategoría
    products = Product.objects.filter(category=subcategory)

    # Obtener valores de precio mínimo y máximo desde la solicitud GET
    price_min = request.GET.get('price_min', 0)  # Valor predeterminado 0
    price_max = request.GET.get('price_max', 10000000)  # Valor predeterminado 10 millones

    # Aplicar filtro de precios si se proporcionan
    products = products.filter(price__gte=price_min, price__lte=price_max)

    context = {
        'subcategory': subcategory,
        'products': products,
        'price_min': price_min,  # Enviar el valor actual al template
        'price_max': price_max,  # Enviar el valor actual al template
    }
    
    return render(request, 'store/products-list.html', context)


def product_detail(request, slug):
    # Obtener el producto actual
    product = get_object_or_404(Product, slug=slug)
    attributes = product.attributes.all()
    # Obtener la subcategoría del producto
    subcategory = product.category

    # Filtrar productos que están en la misma subcategoría y excluye el producto actual
    similar_products = Product.objects.filter(category=subcategory).exclude(id=product.id)
    
    # Seleccionar hasta 6 productos al azar
    similar_products = random.sample(list(similar_products), min(len(similar_products), 6))

    return render(request, 'store/product-detail.html', {
        'product': product,
        'similar_products': similar_products,
        'attributes': attributes,
    })

def services(request):
    services_list = [
        {
            'title': 'Instalación de Sistemas Fotovoltaicos y Equipos de Conectividad',
            'description': 'Ofrecemos instalación profesional y segura de sistemas fotovoltaicos, antenas satelitales y cámaras de seguridad, asegurando que todos los equipos estén correctamente conectados y funcionando. Nuestro equipo de expertos cubre hogares, empresas y áreas rurales, garantizando una instalación rápida, eficiente y con total garantía de funcionamiento.',
            'image': 'images/service1.png',  # Ruta relativa a la carpeta "static"
            'action_text': 'Solicita tu Instalación',
            'action_link': '#'
        },
        {
            'title': 'Consultoría para Proyectos de Energía Solar y Seguridad',
            'description': 'Ofrecemos consultoría personalizada para proyectos de energía solar y seguridad, guiándote en cada paso del proceso de instalación de sistemas solares o equipos de conectividad. Ya sea para tu hogar o empresa, te proporcionamos soluciones a medida para maximizar la eficiencia y el ahorro, con una evaluación detallada de tus necesidades y presupuestos personalizados según tus requerimientos.',
            'image': 'images/service2.png',
            'action_text': 'Solicita tu Asesoría',
            'action_link': '#'
        },
        # Añade más servicios si es necesario
    ]
    return render(request, 'store/services.html', {'services': services_list})

def contact(request):
    return render(request, 'store/contact.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu perfil ha sido actualizado con éxito.")
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'store/edit-profile.html', {'form': form})

@login_required
def my_orders(request):
    # Obtener todas las órdenes que no estén en estado "pending"
    orders = Order.objects.filter(customer=request.user).exclude(status='pending').order_by('-created_at')
    
    # Pasar las órdenes al contexto
    return render(request, 'store/my_orders.html', {'orders': orders})

@login_required
def distributor_orders(request):
    if not request.user.user_type == 2:  # Verificar que es un distribuidor
        return redirect('store')

    distributor_products = request.user.products.all()

    if not distributor_products.exists():
        messages.info(request, "No tienes productos asignados.")
        return redirect('store')

    orders = Order.objects.filter(items__product__in=distributor_products).distinct()

    return render(request, 'store/distributor_orders.html', {'orders': orders})



