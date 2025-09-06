from rest_framework.test import APIClient
from shop.models import Product
from shop.models import ProductOption
from shop.models import Tag
from django.urls import reverse
import pytest

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def product_with_two_options_two_tags(db):
    # Create product (no price field)
    product = Product.objects.create(name="Test Product")
    # Create two options
    option1 = ProductOption.objects.create(product=product, name="Option1", price=1000)
    option2 = ProductOption.objects.create(product=product, name="Option2", price=2000)
    # Create two tags
    tag1 = Tag.objects.create(name="Tag1")
    tag2 = Tag.objects.create(name="Tag2")
    # Assign tags to product (assuming M2M)
    product.tag_set.add(tag1, tag2)
    return {
        "product": product,
        "options": [option1, option2],
        "tags": [tag1, tag2],
    }