# Generated by Django 5.1 on 2024-08-22 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Customer'), (2, 'Distributor'), (3, 'Admin')], null=True),
        ),
    ]
