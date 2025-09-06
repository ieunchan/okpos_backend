import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_products_patch(api_client, product_with_two_options_two_tags):
    # 준비
    product = product_with_two_options_two_tags["product"]
    options = product_with_two_options_two_tags["options"]
    tags = product_with_two_options_two_tags["tags"]
    url = reverse("product-detail", args=[product.id])

    original_option_count = len(options)
    original_tag_count = len(tags)

    patch_data = {
        'name': 'TestProduct',
        'option_set': [
            {'id': options[0].id, 'name': options[0].name, 'price': options[0].price},
            {'id': options[1].id, 'name': 'Updated Option Name', 'price': 9999},
            {'name': 'New Option', 'price': 1234},
            {'id': options[0].id, '_delete': True},
        ],
        'tag_set': [
            {'id': tags[0].id, 'name': tags[0].name},
            {'id': tags[1].id, 'name': 'Updated Tag Name'},
            {'name': 'New Tag'},
        ],
    }

    # 요청 보냄
    response = api_client.patch(url, patch_data, format='json')

    # 검증 시작
    assert response.status_code == 200
    data = response.data
    product.refresh_from_db() 
    assert product.name == 'TestProduct'
    assert 'option_set' in data
    assert len(data['option_set']) == original_option_count
    option_names = [o['name'] for o in data['option_set']]
    option_prices = [o['price'] for o in data['option_set']]
    assert 'Updated Option Name' in option_names
    assert 9999 in option_prices
    assert 'New Option' in option_names
    assert 1234 in option_prices

    # DB 확인 시작
    assert product.option_set.count() == original_option_count
    assert 'tag_set' in data
    tag_names = {t['name'] for t in data['tag_set']}
    assert 'Updated Tag Name' in tag_names
    assert 'New Tag' in tag_names
    assert product.tag_set.count() == original_tag_count + 1
