# Generated by Django 5.1 on 2024-09-01 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_product_brand'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='distributor',
            name='phone_number',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Customer'), (2, 'Distributor'), (3, 'Admin')], default=1, null=True),
        ),
    ]
