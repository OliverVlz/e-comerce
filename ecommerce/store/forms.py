from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser, Product, Distributor, ProductAttribute, AttributeName, Order, OrderItem
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
        fields = ['name', 'description', 'price', 'ref', 'category', 'brand', 'stock', 'image']
        
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
            self.fields['attribute'].widget,  
            ProductAttribute._meta.get_field('attribute').remote_field, 
            admin_site=admin.site, 
            can_add_related=True 
        )

ProductAttributeFormSet = forms.inlineformset_factory(
    Product,
    ProductAttribute,
    form=ProductAttributeForm,
    extra=1,  # Cantidad de formularios adicionales que se mostrarán por defecto
    can_delete=True  
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
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_staff', 'user_type', 'groups', 'user_permissions')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].disabled = True  

        if 'user_type' in self.fields:
            self.fields['user_type'].disabled = True  

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

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'status', 'total_price']  
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
        }

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)

        # Configuración de Crispy Forms (opcional)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('status', css_class='mb-3'),
            Field('total_price', css_class='mb-3', readonly=True),
            Submit('submit', 'Guardar Cambios', css_class='btn btn-primary w-100'),
        )

    def clean_total_price(self):
        if self.instance:
            total = sum(item.get_total_item_price() for item in self.instance.items.all())
            if self.cleaned_data.get('total_price') != total:
                raise ValidationError("El total no coincide con la suma de los artículos.")
        return self.cleaned_data.get('total_price')
    

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
        }

    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        
        # Configuración de Crispy Forms (opcional)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('product', css_class='mb-3'),
            Field('quantity', css_class='mb-3'),
            Field('price', css_class='mb-3', readonly=True),
        )

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        if quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")
        return cleaned_data

