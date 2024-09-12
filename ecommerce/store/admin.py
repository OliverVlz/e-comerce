from django.contrib import admin
from django import forms
from .models import CustomUser, Distributor, Product, Category
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.text import slugify  # Importación para generar slugs automáticamente

User = get_user_model()

# Helper para obtener el queryset filtrado por usuario
def _get_user_queryset(request, qs):
    # Superusuarios pueden ver todo
    if request.user.is_superuser:
        return qs
    # Distribuidores solo ven sus propios datos
    if request.user.user_type == 2:  
        return qs.filter(distributor_profile=request.user.distributor_profile)
    # Clientes pueden ver todos los productos
    if request.user.user_type == 1:  
        return qs
    return qs.none()  # Otros usuarios no ven nada


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('username', 'email', 'user_type', 'is_active', 'is_staff', 'last_login')
    list_filter = ('is_active', 'is_staff', 'user_type', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Distributor Info', {'fields': ('company_name', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type')}),
        ('Groups & Permissions', {'fields': ('groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_staff', 'user_type'),
        }),
    )

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
    user = forms.ModelChoiceField(queryset=User.objects.filter(user_type=2), required=True)

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


class ProductAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return _get_user_queryset(request, qs)

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
        super().save_model(request, obj, form, change)

    list_display = ('name', 'price', 'sku', 'stock', 'distributor', 'category', 'created_at')
    search_fields = ('name', 'sku')
    list_filter = ('category', 'distributor', 'stock', 'created_at')

admin.site.register(Product, ProductAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name',)

    # Generar slug automáticamente a partir del nombre si no está definido
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)

admin.site.register(Category, CategoryAdmin)
