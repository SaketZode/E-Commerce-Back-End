# Generated by Django 3.0.3 on 2021-03-29 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0007_auto_20210329_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='shippingPrice',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='taxPrice',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='totalPrice',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shippingdetails',
            name='shippingPrice',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
