from django.contrib import admin
from MainApp.models import Product, Review, Order, OrderItem, ShippingDetails

admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingDetails)

