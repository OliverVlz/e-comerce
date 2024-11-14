from django.urls import path
from . import views
from django.contrib.auth.views import LoginView 

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('signup/', views.signup, name='signup'), 
    path('login/', LoginView.as_view(template_name='store/login.html'), name='login'),  # URL para login usando LoginView
    path('profile/', views.profile, name='profile'),
    path('distributor-profile/', views.distributor_profile, name='distributor_profile'), 
    path('logout/', views.logout_view, name='logout'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('decrease-quantity/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add-product/', views.add_product, name='add-product'),
    path('distributor-products/', views.distributor_products, name='distributor-products'),
    path('products/', views.products_view, name='products'),
    path('products/<slug:subcategory_slug>/', views.products_list, name='products_list'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('services/', views.services, name='services'),
]