from django.contrib import admin
from django import forms
from .models import CustomUser, Distributor, Product, Category
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

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
        ('Distributor Info', {
            'fields': ('company_name', 'address'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type'),
        }),
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
        if request.user.is_superuser:
            return qs
        if request.user.user_type == 2:  # Distribuidor
            # El distribuidor solo debe ver su propio perfil
            return qs.filter(id=request.user.id)
        if request.user.user_type == 1:  # Cliente
            # El cliente solo debe ver su propio perfil
            return qs.filter(id=request.user.id)
        return qs

    def has_view_permission(self, request, obj=None):
        if request.user.user_type == 2:  # Distribuidor
            # El distribuidor solo puede ver su propio perfil
            return obj is None or obj == request.user
        if request.user.user_type == 1:  # Cliente
            # El cliente solo puede ver su propio perfil
            return obj is None or obj == request.user
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if request.user.user_type == 2:  # Distribuidor
            # El distribuidor solo puede cambiar su propio perfil
            return obj is None or obj == request.user
        if request.user.user_type == 1:  # Cliente
            # El cliente solo puede cambiar su propio perfil
            return obj is None or obj == request.user
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        # Solo los superusuarios pueden agregar usuarios
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        if request.user.user_type in [1, 2]:  # Cliente o Distribuidor
            # Los clientes y distribuidores no deberían poder eliminar sus propios perfiles en el admin
            return False
        return super().has_delete_permission(request, obj)

admin.site.register(CustomUser, CustomUserAdmin)

class DistributorAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.filter(user_type=2), required=True)

    class Meta:
        model = Distributor
        fields = '__all__'

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

    def get_readonly_fields(self, request, obj=None):
        if request.user.user_type == 2:  # Distribuidor
            # El campo 'user' es de solo lectura para los distribuidores
            return ['user']
        return []
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.user_type == 2:  # Distribuidor
            # El distribuidor solo debe ver su propio perfil
            return qs.filter(user=request.user)
        return qs
    
admin.site.register(Distributor, DistributorAdmin)

class ProductAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.user_type == 2:  # Distribuidor
            # Esto filtra los productos para que el distribuidor solo vea los suyos.
            return qs.filter(distributor=request.user.distributor_profile)
        if request.user.user_type == 1:  # Cliente
            # Permitir que los clientes vean todos los productos
            return qs
        return qs.none()

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.user_type in [1, 2]:  # Cliente o Distribuidor
            return True
        return False

    def has_add_permission(self, request):
        # Permitir a superusuarios y distribuidores agregar productos
        return request.user.is_superuser or request.user.user_type == 2

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # Los distribuidores pueden modificar sus propios productos, pero los clientes no
        if request.user.user_type == 2 and obj:
            return obj.distributor == request.user.distributor_profile
        return False  # Los clientes no deberían tener permiso para cambiar productos

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # Los distribuidores pueden eliminar sus propios productos, pero los clientes no
        if request.user.user_type == 2 and obj:
            return obj.distributor == request.user.distributor_profile
        return False  # Los clientes no deberían tener permiso para eliminar productos

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        # Los distribuidores no pueden cambiar el campo distribuidor
        return ['distributor']

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not change:
            # Setear el distribuidor actual para un nuevo producto
            obj.distributor = request.user.distributor_profile
        super().save_model(request, obj, form, change)



    list_display = ('name', 'price', 'sku', 'stock', 'distributor', 'category', 'created_at')
    search_fields = ('name', 'sku')
    list_filter = ('category', 'distributor', 'stock', 'created_at')

admin.site.register(Product, ProductAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name',)  

admin.site.register(Category, CategoryAdmin)
