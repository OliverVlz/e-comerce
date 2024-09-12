from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Distributor
from django.core.exceptions import ValidationError

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
        self.fields['user_type'].disabled = True  

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
