from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, DistributorProfile

class CustomUserCreationForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, required=False)
    status = forms.ChoiceField(choices=[('active', 'Active'), ('inactive', 'Inactive')], required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'user_type', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if user.user_type == 'distributor':
                DistributorProfile.objects.create(
                    user=user,
                    company_name=self.cleaned_data['company_name'],
                    status=self.cleaned_data['status'],
                )
        return user

class CustomUserChangeForm(UserChangeForm):
    company_name = forms.CharField(max_length=255, required=False)
    status = forms.ChoiceField(choices=[('active', 'Active'), ('inactive', 'Inactive')], required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if user.user_type == 'distributor':
                distributor_profile, created = DistributorProfile.objects.get_or_create(user=user)
                distributor_profile.company_name = self.cleaned_data['company_name']
                distributor_profile.status = self.cleaned_data['status']
                distributor_profile.save()
        return user
