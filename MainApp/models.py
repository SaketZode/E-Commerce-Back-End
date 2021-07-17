from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, null=False, blank=False)
    image = models.ImageField(null=True, blank=True, upload_to='images/')
    brand = models.CharField(max_length=150, null=True, blank=True)
    category = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(max_length=550, null=False, blank=False)
    rating = models.FloatField( null=True, blank=True)
    numReviews = models.IntegerField(null=True, blank=True)
    price = models.FloatField(null=False, blank=False)
    countInStock = models.IntegerField(null=False, blank=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    id = models.AutoField(primary_key=True, editable=False)

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    comment = models.CharField(max_length=250, null=True, blank=True)
    id = models.AutoField(primary_key=True, editable=False)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    paymentMethod = models.CharField(max_length=50, null=True, blank=True)
    taxPrice = models.FloatField(null=True, blank=True)
    shippingPrice = models.FloatField(null=True, blank=True)
    totalPrice = models.FloatField(null=True, blank=True)
    isPaid = models.BooleanField(default=False)
    paidAt = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    isDelivered = models.BooleanField(default=False)
    deliveredAt = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    id = models.AutoField(primary_key=True, editable=False)

    def __str__(self):
        return str(self.createdAt)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    id = models.AutoField(primary_key=True, editable=False)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name


class ShippingDetails(models.Model):
    order = models.OneToOneField(Order, related_name='shippingAddress', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    postalCode = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    shippingPrice = models.FloatField(null=True, blank=True)
    id = models.AutoField(primary_key=True, editable=False)

    def __str__(self):
        return self.address
