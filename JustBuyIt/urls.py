"""JustBuyIt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from MainApp import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/profile/', views.getUserProfile, name='user_profile'),
    path('bestproducts/', views.getTopProducts, name='top-products'),
    path('products/', views.getProducts, name='product_list'),
    path('product/create/', views.createProduct, name='create-product'),
    path('products/<int:productId>', views.getProduct, name='product_details'),
    path('product/delete/<int:id>', views.deleteProduct, name='delete-product'),
    path('product/update/<int:id>', views.updateProductDetails, name='update-product'),
    path('product/image/upload/', views.uploadProductImage, name='upload-product-image'),
    path('product/review/create/<int:product_id>', views.createProductReview, name='create-product-review'),
    path('user/login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/register/', views.registerUser, name='register_user'),
    path('user/profile/update/', views.updateUserProfile, name='update_user_profile'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('user/list/', views.getUsers, name='user_list'),
    path('user/delete/<int:id>', views.deleteUser, name='delete_user'),
    path('user/details/<int:id>', views.getUserById, name='user-details'),
    path('user/update/<int:id>', views.updateUserDetails, name='update-user'),
    path('order/place/', views.createOrder, name='place-order'),
    path('order/details/<int:pk>', views.getOrderById, name='order-details'),
    path('order/<int:orderId>/pay/', views.updateOrderStatusToPaid, name='payment-status'),
    path('order/history/', views.getOrderHistory, name='order-history'),
    path('orders/', views.getAllOrders, name='orders-list'),
    path('order/deliver/<int:id>', views.updateOrderToDelivered, name='deliver-order'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
