from django.contrib import admin
from .models import CustomUser, Distributor, Product, Category
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    # Campos que se muestran en la lista de usuarios en el administrador
    list_display = ('username', 'email', 'user_type', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'user_type')

    # Campos que se muestran cuando se edita un usuario
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'user_type', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Campos que se muestran cuando se agrega un usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'user_type', 'groups', 'user_permissions'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)


# Configurar el administrador para Distribuidores
class DistributorAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'phone_number', 'status')
    search_fields = ('company_name', 'email')
    list_filter = ('status',)

admin.site.register(Distributor, DistributorAdmin)

# Configurar el administrador para Productos
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'sku', 'stock', 'distributor')
    search_fields = ('name', 'sku')
    list_filter = ('category', 'distributor')

admin.site.register(Product, ProductAdmin)

# Configurar el administrador para Categorías
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Category, CategoryAdmin)
