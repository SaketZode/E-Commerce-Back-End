from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage
from rest_framework import status, pagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from MainApp.models import Product, Order, ShippingDetails, OrderItem, Review
from MainApp.serializers import ProductSerializer, UserSerializer, UserSerializerWithToken, OrderSerializer, ProductDetailSerializer
from rest_framework.response import Response
from datetime import datetime
from rest_framework.pagination import PageNumberPagination


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data['username'] = self.user.username
        data['email'] = self.user.email
        data['id'] = self.user.id
        data['isAdmin'] = self.user.is_staff

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


class MyCustomPagination(PageNumberPagination):

    def get_from(self):
        return int((self.page.paginator.per_page * self.page.number) - self.page.paginator.per_page + 1)

    def get_to(self):
        return self.get_from() + int(len(self.page.object_list)) - 1

    def get_paginated_response(self, data):

        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'per_page': self.page.paginator.per_page,
            'from': self.get_from(),
            'to': self.get_to(),
            'results': data
        })


@api_view(['GET'])
def getProducts(request):
    search_key = request.query_params.get('searchtext')

    if search_key is None:
        search_key = ''

    paginator = MyCustomPagination()
    paginator.page_size = 8

    products = Product.objects.filter(name__icontains=search_key)
    result = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(result, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def getProduct(request, productId):
    try:
        product = Product.objects.get(id=productId)
        serializer = ProductDetailSerializer(product, many=False)
        return Response(serializer.data)
    except:
        errMsg = "Product with id {} does not exist".format(productId)
        message = {'detail': errMsg}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def getTopProducts(request):
    top_products = Product.objects.filter(rating__gte=4).order_by('-rating')
    serializer = ProductSerializer(top_products, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def createProduct(request):
    data = request.data
    try:
        product = Product.objects.create(
            user=request.user,
            name=data['name'],
            brand=data['brand'],
            category=data['category'],
            description=data['description'],
            price=data['price'],
            countInStock=data['countInStock'],
            image=request.FILES.get('image')
        )

        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except:
        return Response({'detail': 'Failed to create product'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def uploadProductImage(request):
    try:
        data = request.data

        product_id = data['product_id']
        product = Product.objects.get(id=product_id)
        product.image = request.FILES.get('image')
        print(product.image)
        product.save()

        return Response({'detail': 'Image uploaded successfully'}, status=status.HTTP_200_OK)
    except:
        return Response({'detail': 'Image upload failed'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    pagination = MyCustomPagination()
    pagination.page_size = 1
    users = User.objects.all()
    result = pagination.paginate_queryset(users, request)
    serializer = UserSerializer(result, many=True)
    return pagination.get_paginated_response(serializer.data)


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
            return Response({'detail': 'You are not authorized to view this order'},
                            status=status.HTTP_401_UNAUTHORIZED)

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
    pagination = MyCustomPagination()
    pagination.page_size = 10

    try:
        orders = user.order_set.all()
        result = pagination.paginate_queryset(orders, request)
        serializer = OrderSerializer(result, many=True)
        return pagination.get_paginated_response(serializer.data)
    except:
        return Response({'detail': 'Invalid user credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getAllOrders(request):
    paginator = MyCustomPagination()
    paginator.page_size = 7

    orders = Order.objects.all()
    result = paginator.paginate_queryset(orders, request)
    serializer = OrderSerializer(result, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateOrderToDelivered(request, id):
    try:
        order = Order.objects.get(id=id)
        order.isDelivered = True
        order.deliveredAt = datetime.now()
        order.save()
        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except:
        return Response({'detail': 'Unexpected error occurred while updating order status'},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteUser(request, id):
    try:
        userToDelete = User.objects.get(id=id)
        userToDelete.delete()
        return Response({'detail': 'User deleted successfully'}, status=status.HTTP_200_OK)
    except:
        return Response({'detail': 'Failed to delete user'}, status=status.HTTP_417_EXPECTATION_FAILED)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUserById(request, id):
    try:
        user = User.objects.get(id=id)
        serialized_data = UserSerializer(user, many=False)
        return Response(serialized_data.data)
    except:
        return Response({'detail': 'Failed to find user with given id'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateUserDetails(request, id):
    try:
        user = User.objects.get(id=id)

        data = request.data
        user.first_name = data['name']
        user.email = data['email']
        user.username = data['username']
        user.is_staff = data['isAdmin']

        serializer = UserSerializer(user, many=False)
        user.save()

        return Response(serializer.data)
    except:
        msg = {"detail": "Failed to update user details"}
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateProductDetails(request, id):
    try:
        product = Product.objects.get(id=id)

        data = request.data
        print(data)
        product.name = data['name']
        product.price = data['price']
        product.brand = data['brand']
        product.description = data['description']
        product.category = data['category']
        product.countInStock = data['countInStock']
        #product.image = data['image']

        serializer = ProductSerializer(product, many=False)
        product.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    except:
        return Response({'detail': 'Unexpected error occurred while updating product details'},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteProduct(request, id):
    try:
        product = Product.objects.get(id=id)
        product.delete()
        return Response({'detail': 'Successfully deleted product'},
                        status=status.HTTP_200_OK)
    except:
        return Response({'detail': 'Unexpected error occurred while deleting product'},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def createProductReview(request, product_id):
    user = request.user
    product = Product.objects.get(id=product_id)

    data = request.data

    alreadyExists = product.review_set.filter(user=user).exists()

    if alreadyExists:
        return Response({'detail': 'You have already reviewed the product'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    elif data['rating'] == 0:
        return Response({'detail': 'Please provide appropriate rating'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        review = Review.objects.create(
            user=user,
            product=product,
            rating=data['rating'],
            comment=data['comment'],
            name=data['name']
        )

        reviews = product.review_set.all()
        product.numReviews = len(reviews)

        total = 0

        for user_review in reviews:
            total += user_review.rating

        product.rating = total/len(reviews)

        product.save()

        return Response({'detail': 'Review successfully recorded'}, status=status.HTTP_201_CREATED)
