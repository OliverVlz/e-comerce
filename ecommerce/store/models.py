from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.exceptions import ValidationError
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

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.username

class Distributor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='distributor_profile')
    company_name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = 'Distribuidor'
        verbose_name_plural = 'Distribuidores'

    def __str__(self):
        return self.company_name

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')  # Para subcategorías
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.name

    @property
    def is_subcategory(self):
        return self.parent is not None
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Generar slug basado en el nombre
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    ref = models.CharField(max_length=50, unique=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, related_name="products")
    brand = models.CharField(max_length=100, default='No brand')
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)

    is_featured = models.BooleanField(default=False, verbose_name="¿Es destacado?")
    featured_order = models.PositiveIntegerField(
        blank=True, 
        null=True, 
        verbose_name="Orden destacado (1-8)",
        help_text="Define la posición del producto destacado (1-8)"
    )

    is_discounted = models.BooleanField(default=False, verbose_name="¿Está en descuento?")
    discounted_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,  
        blank=True, 
        null=True, 
        verbose_name="Precio con descuento"
    )
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        verbose_name="Porcentaje de descuento (%)",
        help_text="Porcentaje de descuento aplicado al producto (calculado automáticamente, no es necesario ingresar este valor)"
    )   
        
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def clean(self):
        if self.is_featured and self.featured_order is None:
            raise ValidationError("Si el producto es destacado, debe tener un número de orden (1-8).")
        # Validación: El número de orden debe estar entre 1 y 8 si es destacado.
        if self.featured_order and (self.featured_order < 1 or self.featured_order > 9):
            raise ValidationError("El número de orden debe estar entre 1 y 8.")
        # Validar que `featured_order` sea único entre los productos destacados
        if self.is_featured and self.featured_order:
            if Product.objects.filter(is_featured=True, featured_order=self.featured_order).exclude(id=self.id).exists():
                raise ValidationError({
                    'featured_order': f'El valor "{self.featured_order}" ya está asignado a otro producto destacado. Elija un valor único entre 1 y 8.'
                })
        if self.price < 0:
            raise ValidationError('El precio no puede ser negativo.')
        if self.stock < 0:
            raise ValidationError('El stock no puede ser negativo.')
        if self.is_discounted and self.discounted_price is not None:
            if self.discounted_price >= self.price:
                raise ValidationError("El precio con descuento debe ser menor al precio original.")

    def save(self, *args, **kwargs):
        self.clean()
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

        # Si hay un precio con descuento, calcula el porcentaje
        if self.is_discounted and self.discounted_price:
            self.discount_percentage = (
                ((self.price - self.discounted_price) / self.price) * 100
            )
        else:
            self.discounted_price = None
            self.discount_percentage = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class AttributeName(models.Model):
    name = models.CharField(max_length=255)

    class Meta: 
        verbose_name = 'Nombre de Atributo'
        verbose_name_plural = 'Nombres de Atributos'

    def __str__(self):
        return self.name

class ProductAttribute(models.Model):
    attribute = models.ForeignKey(AttributeName, on_delete=models.CASCADE, default=1)
    value = models.CharField(max_length=255)
    product = models.ForeignKey('Product', related_name='attributes', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'

    def __str__(self):
        return f"Order {self.id} - {self.customer.username} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        
        if self.pk:
            self.total_price = self.get_total_price()
        super().save(*args, **kwargs)

    def get_total_price(self):
        if not self.pk or not self.items.exists():
            return 0
        
        total = sum(
            item.get_total_item_price() 
            for item in self.items.all() 
            if item.product.is_active  # Excluir productos no activos
        )
        return total

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    def get_total_item_price(self):
        return self.quantity * self.price
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualizar el precio total de la orden después de guardar este item
        self.order.save()