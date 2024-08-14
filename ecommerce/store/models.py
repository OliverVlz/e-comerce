from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    user_type = models.CharField(max_length=20, choices=[
        ('customer', 'Customer'),
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    ])
