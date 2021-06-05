from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from MainApp.models import Product, Order, ShippingDetails, OrderItem
from MainApp.serializers import ProductSerializer, UserSerializer, UserSerializerWithToken, OrderSerializer
from rest_framework.response import Response
from datetime import datetime


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data['username'] = self.user.username
        data['email'] = self.user.email
        data['id'] = self.user.id

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['POST'])
def registerUser(request):
    data = request.data

    try:
        user = User.objects.create(
            first_name=data['name'],
            email=data['email'],
            password=make_password(data['password']),
            username=data['username']
        )

        serializer = UserSerializerWithToken(user, many=False)
        return Response(serializer.data)
    except:
        message = {'detail': 'User with this email already exists'}
        return Response(message, status=status.HTTP_409_CONFLICT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    try:
        user = request.user
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    except:
        message = {'detail': 'Failed to fetch user profile'}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    try:
        user = request.user
        serializer = UserSerializerWithToken(user, many=False)

        data = request.data
        user.first_name = data['name']
        user.email = data['email']
        user.username = data['username']

        if data['password'] != '':
            user.password = make_password(data['password'])

        user.save()
    except:
        msg = {"detail": "Failed to update user profile"}
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.data)


@api_view(['GET'])
def getProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getProduct(request, productId):
    try:
        product = Product.objects.get(id=productId)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)
    except:
        errMsg = "Product with id {} does not exist".format(productId)
        message = {'detail': errMsg}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createOrder(request):
    user = request.user
    data = request.data

    orderItems = data['orderItems']

    if len(orderItems) == 0:
        return Response({'detail': 'No items to place order'}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        user=user,
        paymentMethod=data['paymentMethod'],
        taxPrice=data['tax'],
        shippingPrice=data['shippingPrice'],
        totalPrice=data['total']
    )

    shipping = ShippingDetails.objects.create(
        order=order,
        address=data['shippingAddress']['address'],
        city=data['shippingAddress']['city'],
        postalCode=data['shippingAddress']['zipcode'],
        country=data['shippingAddress']['country'],
    )

    for i in orderItems:
        product = Product.objects.get(id=i['product'])

        item = OrderItem.objects.create(
            product=product,
            order=order,
            name=product.name,
            quantity=i['qty'],
            price=i['price'],
            image=product.image.url
        )

        product.countInStock -= item.quantity
        product.save()

    serializer = OrderSerializer(order, many=False)

    print('returning ', serializer.data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):
    user = request.user

    try:
        order = Order.objects.get(id=pk)

        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            print(serializer.data)
            return Response(serializer.data)
        else:
            return Response({'detail': 'You are not authorized to view this order'}, status=status.HTTP_401_UNAUTHORIZED)

    except:
        return Response({'detail': 'Order with given ID does not exist'})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderStatusToPaid(request, orderId):
    try:
        order = Order.objects.get(id=orderId)
        order.isPaid = True
        order.paidAt = datetime.now()
        order.save()
        return Response({'detail': 'Payment successful'}, status=status.HTTP_200_OK)
    except:
        return Response({'detail': 'Payment failed'}, status=status.HTTP_402_PAYMENT_REQUIRED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderHistory(request):
    user = request.user

    try:
        orders = user.order_set.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    except:
        return Response({'detail': 'Invalid user credentials'}, status=status.HTTP_401_UNAUTHORIZED)

