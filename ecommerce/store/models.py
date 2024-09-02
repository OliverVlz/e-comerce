from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
#from phonenumber_field.modelfields import PhoneNumberField
    
# Modelo de Usuario Personalizado
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        (1, 'Customer'),
        (2, 'Distributor'),
        (3, 'Admin'),
    ]

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, null=True, default=1)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.username

class Distributor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='distributor_profile')
    company_name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


    def __str__(self):
        return self.company_name

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, related_name="products")
    brand = models.CharField(max_length=100, default='No brand')
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


    power_rating = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Power rating in watts (W)")
    voltage = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Operating voltage in volts (V)")
    efficiency = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Efficiency as a percentage")
    dimensions = models.CharField(max_length=100, default='0000x000x00', help_text="Dimensions in mm, e.g., 1650x992x35")
    weight = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Weight in kilograms (kg)")

    def __str__(self):
        return self.name
