# Generated by Django 5.1 on 2024-12-10 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_product_discount_percentage_product_discounted_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='featured_order',
            field=models.PositiveIntegerField(blank=True, help_text='Define la posición del producto destacado (1-8)', null=True, verbose_name='Orden destacado (1-8)'),
        ),
        migrations.AddField(
            model_name='product',
            name='is_featured',
            field=models.BooleanField(default=False, verbose_name='¿Es destacado?'),
        ),
    ]
