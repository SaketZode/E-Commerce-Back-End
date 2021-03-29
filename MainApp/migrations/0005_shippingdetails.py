# Generated by Django 3.0.3 on 2021-03-28 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0004_orderitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShippingDetails',
            fields=[
                ('address', models.CharField(blank=True, max_length=300, null=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('postalCode', models.CharField(blank=True, max_length=50, null=True)),
                ('country', models.CharField(blank=True, max_length=50, null=True)),
                ('shippingPrice', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('order', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='MainApp.Order')),
            ],
        ),
    ]
