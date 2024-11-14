from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser, Product, Distributor, ProductAttribute, AttributeName
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Field, Div, HTML, ButtonHolder
from django.forms import modelformset_factory
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib import admin

"""Formulario para registro de usuarios"""

class UserSignupForm(UserCreationForm):
    usable_password = None
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar Contraseña'}),
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nombre de Usuario'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo Electrónico'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Apellido'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserSignupForm, self).__init__(*args, **kwargs)
        
        # Aplicar solo la clase 'form-control floating-label-input' a todos los campos
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control floating-label-input'
        
        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                Field('username', css_class='mb-3'),
                Field('email', css_class='mb-3'),
                Field('first_name', css_class='mb-3'),
                Field('last_name', css_class='mb-3'),
                Field('password1', css_class='mb-3'),
                Field('password2', css_class='mb-3'),
                Submit('submit', 'Registrarse', css_class='btn btn-primary w-100'),
                css_class='card-body'
            ),
        )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')
        return email
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control floating-label-input',
            'placeholder': 'Nombre de Usuario',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control floating-label-input',
            'placeholder': 'Contraseña',
        })
    )

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'sku', 'category', 'brand', 'stock', 'image']
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
class ProductAttributeForm(forms.ModelForm):
    attribute = forms.ModelChoiceField(
        queryset=AttributeName.objects.all(),  # Permitir seleccionar un atributo existente
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label="Attribute Name"
    )
    value = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter value'}),
        label="Value",
        required=True
    )

    class Meta:
        model = ProductAttribute
        fields = ['attribute', 'value']
    
    def __init__(self, *args, **kwargs):
        super(ProductAttributeForm, self).__init__(*args, **kwargs)

        # Agregar el widget RelatedFieldWidgetWrapper para obtener los botones de agregar/editar/ver
        self.fields['attribute'].widget = RelatedFieldWidgetWrapper(
            self.fields['attribute'].widget,  # El widget del campo
            ProductAttribute._meta.get_field('attribute').remote_field,  # Relación con el modelo AttributeName
            admin_site=admin.site,  # Admin site que gestiona este modelo
            can_add_related=True  # Para que se muestre el botón "+"
        )

ProductAttributeFormSet = forms.inlineformset_factory(
    Product,
    ProductAttribute,
    form=ProductAttributeForm,
    extra=1,  # Cantidad de formularios adicionales que se mostrarán por defecto
    can_delete=True  # Permitir eliminar atributos también
)

"""Formulario para panel de administración de usuarios"""
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_staff', 'user_type', 'groups', 'user_permissions')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('A user with that email already exists.')
        return email

class CustomUserChangeForm(UserChangeForm):
    company_name = forms.CharField(max_length=255, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_staff', 'user_type', 'groups', 'user_permissions')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].disabled = True  

        # Verifica si 'user_type' está en los campos antes de deshabilitarlo
        if 'user_type' in self.fields:
            self.fields['user_type'].disabled = True  

        # Configura los campos iniciales relacionados con el perfil de distribuidor
        if self.instance and hasattr(self.instance, 'distributor_profile'):
            distributor = self.instance.distributor_profile
            self.fields['company_name'].initial = distributor.company_name
            self.fields['address'].initial = distributor.address

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if hasattr(user, 'distributor_profile'):
                distributor = user.distributor_profile
                distributor.company_name = self.cleaned_data.get('company_name', distributor.company_name)
                distributor.address = self.cleaned_data.get('address', distributor.address)
                distributor.save()
        return user

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        return phone_number.strip() if phone_number else ''

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
        }