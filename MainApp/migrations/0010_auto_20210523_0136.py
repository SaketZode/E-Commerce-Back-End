# Generated by Django 3.0.3 on 2021-05-22 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0009_orderitem_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingdetails',
            name='order',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shippingAddress', to='MainApp.Order'),
        ),
    ]
