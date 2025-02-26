from django.contrib import admin
from django import forms
from .models import * 
from .forms import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.text import slugify 

User = get_user_model()

# Helper para obtener el queryset filtrado por usuario
def _get_user_queryset(request, qs):
    # Superusuarios pueden ver todo
    if request.user.is_superuser:
        return qs

    # Si el queryset es de CustomUser (en el caso de la vista de usuarios)
    if qs.model == CustomUser:
        if request.user.user_type == 2:  # Distribuidor
            return qs.filter(id=request.user.id)  # Solo permite ver su propio usuario
        elif request.user.user_type == 1:  # Cliente
            return qs  # Los clientes pueden ver todos los usuarios (o se puede personalizar)

    # Si el queryset es de Product (en el caso de la vista de productos)
    if qs.model == Product:
        if request.user.user_type == 2:  # Distribuidor
            return qs.filter(distributor=request.user.distributor_profile)  # Solo permite ver sus productos

    # Otros usuarios no ven nada
    return qs.none()

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm  # Formulario al agregar
    form = CustomUserChangeForm       # Formulario al editar
    model = CustomUser

    list_display = ('username', 'email', 'user_type', 'is_active', 'is_staff', 'last_login')
    list_filter = ('is_active', 'is_staff', 'user_type', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    base_fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    superuser_fieldsets = base_fieldsets + (
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type')}),
        ('Groups & Permissions', {'fields': ('groups', 'user_permissions')}),
    )

    add_fieldsets = (
        ("Información de inicio de sesión", {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ("Información personal", {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'phone_number'),
        }),
        ("Permisos", {
            'classes': ('wide',),  
            'fields': ('is_active', 'is_staff', 'user_type'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        # Si se está agregando un usuario, usa add_fieldsets
        if obj is None:
            return self.add_fieldsets
        # Si el usuario es un superusuario, muestra todos los campos de permisos
        if request.user.is_superuser:
            return self.superuser_fieldsets
        # Si el usuario no es superusuario, oculta los campos de permisos
        return self.base_fieldsets


    def get_readonly_fields(self, request, obj=None):
        # Para distribuidores, hacer los campos de permisos de solo lectura
        if request.user.user_type == 2:  # Distribuidor
            return ['is_staff', 'is_superuser', 'user_type', 'groups', 'user_permissions']
        # Para otros usuarios (excepto superusuarios), permitir modificar solo sus datos
        return super().get_readonly_fields(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return _get_user_queryset(request, qs)

    # Solo pueden ver su propio perfil, excepto superusuarios
    def has_view_permission(self, request, obj=None):
        if request.user.user_type in [1, 2]:  # Cliente o Distribuidor
            return obj is None or obj == request.user
        return super().has_view_permission(request, obj)

    # Solo pueden modificar su propio perfil, excepto superusuarios
    def has_change_permission(self, request, obj=None):
        if request.user.user_type in [1, 2]:  # Cliente o Distribuidor
            return obj is None or obj == request.user
        return super().has_change_permission(request, obj)

    # Solo superusuarios pueden agregar usuarios
    def has_add_permission(self, request):
        return request.user.is_superuser

    # Clientes y distribuidores no pueden eliminar perfiles
    def has_delete_permission(self, request, obj=None):
        if request.user.user_type in [1, 2]:  # Cliente o Distribuidor
            return False
        return super().has_delete_permission(request, obj)

admin.site.register(CustomUser, CustomUserAdmin)


class DistributorAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.filter(user_type=2), required=True)

    class Meta:
        model = Distributor
        fields = '__all__'

    # Validación para asegurar que el usuario es un distribuidor
    def clean_user(self):
        user = self.cleaned_data.get('user')
        if user.user_type != 2:
            raise forms.ValidationError("El usuario seleccionado no es un distribuidor.")
        return user

class DistributorAdmin(admin.ModelAdmin):
    form = DistributorAdminForm
    list_display = ('user', 'company_name', 'is_active', 'created_at', 'updated_at')
    search_fields = ('company_name',)
    list_filter = ('is_active',)
    fieldsets = (
        (None, {'fields': ('user', 'company_name', 'address', 'is_active')}),
    )

    # El campo 'user' es de solo lectura para distribuidores
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:  # Superusuario puede modificar todo
            return []
        if request.user.user_type == 2:  # Distribuidor solo puede ver el campo 'user' como lectura
            return ['user']
        return []  # Otros roles pueden ver todo


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:  # Superusuarios ven todo
            return qs
        if request.user.user_type == 2:  # Distribuidor solo ve su propio perfil
            return qs.filter(user=request.user)
        return qs.none()  # Otros usuarios no pueden ver nada


admin.site.register(Distributor, DistributorAdmin)
class AttributeNameAdmin(admin.ModelAdmin):
    list_display = ['name']  
    search_fields = ['name'] 

admin.site.register(AttributeName, AttributeNameAdmin)
class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    form = ProductAttributeForm
    extra = 1  # Muestra un formulario en blanco adicional
    can_delete = True  # Permite eliminar atributos

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Filtrar atributos solo para los productos que pertenecen al distribuidor
        if request.user.user_type == 2:  # Si es distribuidor
            return qs.filter(product__distributor=request.user.distributor_profile)
        return qs
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'ref', 'price', 'is_discounted', 'discounted_price', 'discount_percentage', 'is_featured', 'featured_order','slug','is_active', 'stock', 'category', 'created_at')
    search_fields = ('name', 'slug', 'ref', 'is_active')
    list_filter = ('category', 'distributor', 'is_discounted', 'is_featured', 'stock', 'created_at')
    list_editable = ('is_active','is_discounted', 'discounted_price')
    inlines = [ProductAttributeInline]

    def get_readonly_fields(self, request, obj=None):
        # Hacer que el porcentaje de descuento sea solo lectura
        readonly_fields = ['discount_percentage']
        return readonly_fields
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return _get_user_queryset(request, qs)

    # Solo permitir subcategorías en el campo 'category'
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            # Filtrar solo subcategorías (las que tienen parent)
            kwargs["queryset"] = Category.objects.filter(parent__isnull=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    # Los clientes, distribuidores y superusuarios pueden ver los productos
    def has_view_permission(self, request, obj=None):
        return request.user.user_type in [1, 2] or request.user.is_superuser

    # Solo superusuarios y distribuidores pueden agregar productos
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.user_type == 2

    # Solo distribuidores pueden cambiar sus propios productos
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.user_type == 2 and obj:
            return obj.distributor == request.user.distributor_profile
        return False

    # Distribuidores solo pueden eliminar sus propios productos
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.user_type == 2 and obj:
            return obj.distributor == request.user.distributor_profile
        return False

    # Los distribuidores no pueden cambiar el campo 'distributor'
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return ['distributor']

    # Asignar distribuidor automáticamente al crear un nuevo producto
    def save_model(self, request, obj, form, change):
        if request.user.user_type == 2:
            if not change:  # Si está creando un nuevo producto
                obj.distributor = request.user.distributor_profile
            elif obj.distributor != request.user.distributor_profile:  # Intento de cambiar distribuidor
                raise forms.ValidationError("No puedes cambiar el distribuidor de un producto.")
        if not obj.slug:
            obj.slug = slugify(obj.name)

        if obj.is_featured:
            featured_count = Product.objects.filter(is_featured=True).exclude(pk=obj.pk).count()
            if featured_count > 9:
                raise ValueError("No puedes tener más de 8 productos destacados.")
        super().save_model(request, obj, form, change)

        

admin.site.register(Product, ProductAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active', 'image')
    search_fields = ('name', 'slug', 'is_active')
    list_filter = ('parent', 'is_active',)
    list_editable = ('is_active',)

    # Generar slug automáticamente a partir del nombre si no está definido
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)

    # Permitir que distribuidores puedan ver categorías
    def has_view_permission(self, request, obj=None):
        if request.user.user_type == 2 or request.user.is_superuser:
            return True
        return False

    # Permitir que distribuidores puedan cambiar categorías
    def has_change_permission(self, request, obj=None):
        if request.user.user_type == 2 or request.user.is_superuser:
            return True
        return False

    # Permitir que distribuidores puedan agregar categorías
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.user_type == 2

    # Permitir que distribuidores puedan eliminar categorías
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.user_type == 2

    # Opcional: puedes limitar los campos que pueden editar los distribuidores
    def get_readonly_fields(self, request, obj=None):
        if request.user.user_type == 2:  # Distribuidores
            return ['parent']  # Ejemplo: no pueden cambiar el campo 'parent'
        return []

admin.site.register(Category, CategoryAdmin)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    form = OrderItemForm
    extra = 1  # Mostrar un formulario vacío adicional para agregar nuevos artículos
    can_delete = True  # Permitir eliminar artículos

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.user_type == 2:  # Distribuidor
            return qs.filter(product__distributor=request.user.distributor_profile)
        return qs

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderForm
    list_display = ('id', 'customer', 'status', 'total_price', 'created_at', 'updated_at', 'get_order_items')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'id')
    readonly_fields = ('total_price',)
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.user_type == 2:  # Distribuidor
            return qs.filter(items__product__distributor=request.user.distributor_profile).distinct()
        return qs.none()

    def get_order_items(self, obj):
        """Devuelve un resumen de los productos en la orden."""
        return ", ".join([f"{item.product.name} ({item.quantity})" for item in obj.items.all()])
    get_order_items.short_description = "Items"

  
    def save_model(self, request, obj, form, change):
        # Calcular y establecer el precio total antes de guardar
        obj.total_price = obj.get_total_price()
        super().save_model(request, obj, form, change)
    
