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

    list_display = ('username', 'email', 'user_type', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'user_type')
    search_fields = ('username', 'email')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'user_type', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_staff', 'user_type'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

class DistributorAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.filter(user_type='distributor'), required=True)

    class Meta:
        model = Distributor
        fields = '__all__'

class DistributorAdmin(admin.ModelAdmin):
    form = DistributorAdminForm
    list_display = ('company_name', 'phone_number', 'status')
    search_fields = ('company_name',)
    list_filter = ('status',)
    fieldsets = (
        (None, {'fields': ('user', 'company_name', 'phone_number', 'address', 'status')}),
    )

admin.site.register(Distributor, DistributorAdmin)

class ProductAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        if request.user.is_authenticated:
            return request.user.user_type != 'customer'
        return False

    list_display = ('name', 'price', 'sku', 'stock', 'distributor')
    search_fields = ('name', 'sku')
    list_filter = ('category', 'distributor')

admin.site.register(Product, ProductAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Category, CategoryAdmin)