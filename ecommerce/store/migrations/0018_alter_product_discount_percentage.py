# Generated by Django 5.1 on 2024-12-10 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_product_featured_order_product_is_featured'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discount_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Porcentaje de descuento aplicado al producto (calculado automáticamente, no es necesario ingresar este valor)', max_digits=5, null=True, verbose_name='Porcentaje de descuento (%)'),
        ),
    ]