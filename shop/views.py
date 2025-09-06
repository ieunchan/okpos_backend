from rest_framework.viewsets import ModelViewSet
from shop.models import Product
from shop.serializers import ProductSerializer

class ProductViewSet(ModelViewSet):
    
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.all()