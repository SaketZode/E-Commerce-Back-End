from rest_framework.decorators import api_view
from MainApp.models import Product
from MainApp.serializers import ProductSerializer
from rest_framework.response import Response


@api_view(['GET'])
def getProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)
