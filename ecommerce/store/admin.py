from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DistributorProfile
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('username', 'email', 'user_type', 'is_active', 'is_staff', 'company_name')

    list_filter = ('is_active', 'is_staff', 'user_type')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'user_type')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'phone_number', 'company_name', 'status'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:  # Si el objeto no existe, significa que estamos creando un nuevo usuario
            return self.add_fieldsets
        else:  # Si el objeto existe, estamos editando un usuario existente
            fieldsets = list(self.fieldsets)
            if obj.user_type == 'distributor':
                fieldsets.append(
                    ('Distributor Info', {'fields': ('company_name', 'status')})
                )
            return fieldsets

    def save_model(self, request, obj, form, change):
        if not change and obj.user_type == 'distributor':
            obj.is_staff = True
        super().save_model(request, obj, form, change)
        if obj.user_type == 'distributor':
            distributor_profile, created = DistributorProfile.objects.get_or_create(user=obj)
            distributor_profile.company_name = form.cleaned_data['company_name']
            distributor_profile.status = form.cleaned_data['status']
            distributor_profile.save()

    def company_name(self, obj):
        if hasattr(obj, 'distributor_profile'):
            return obj.distributor_profile.company_name
        return None
    company_name.short_description = 'Company Name'

    def status(self, obj):
        if hasattr(obj, 'distributor_profile'):
            return obj.distributor_profile.status
        return None
    status.short_description = 'Status'

admin.site.register(CustomUser, CustomUserAdmin)
