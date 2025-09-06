import pytest
from django.urls import reverse
from shop.models import ProductOption
from shop.models import Product
from shop.models import Tag

@pytest.mark.django_db
def test_products_post(api_client):
    exist = Tag.objects.create(name='Existing Tag')
    url = reverse('product-list')

    request_data = {
        'name': 'Test Product',
        'option_set': [
            {'name': 'TestOption1', 'price': 1000},
            {'name': 'TestOption2', 'price': 2000},
            {'name': 'TestOption3', 'price': 3000}
        ],
        'tag_set': [
            {'pk': exist.pk, 'name': 'Existing Tag'},
            {'name': 'New Tag'}
        ]
    }
    response_data = api_client.post(url, request_data, format='json')

    assert response_data.status_code == 201
    assert response_data.data['name'] == request_data['name']
    assert len(response_data.data['option_set']) == len(request_data['option_set'])
    assert len(response_data.data['tag_set']) == len(request_data['tag_set'])
    assert response_data.data['tag_set'][0]['name'] == exist.name
    assert response_data.data['tag_set'][1]['name'] == request_data['tag_set'][1]['name']

@pytest.mark.django_db
def test_products_post_invalid_data_type(api_client):
    url = reverse('product-list')
    request_data = {
        'name': 123,
        'option_set':[
            {'name': 321, 'price': 'String'},
            {'name': 'String', 'price': 2000},
        ],
        'tag_set':[
            {'pk': 'StringPK', 'name': 'StringTAG'},
        ]
    }
    response_data = api_client.post(url, request_data, format='json')

    # 1) 400 응답 확인
    assert response_data.status_code == 400
    errors = response_data.data
    
    # 2) option_set 에러 메시지 확인
    assert 'option_set' in errors
    assert isinstance(errors['option_set'], list) # option_set 응답값이 리스트인가?
    first_option_error = errors['option_set'][0] # 잘못된 요청값은 0번 인덱스임
    assert 'price' in first_option_error

    # 3) tag_set 에러 메시지 확인

    assert 'tag_set' in errors
    assert isinstance(errors['tag_set'], list)  # 리스트 구조인지 확인
    first_tag_error = errors['tag_set'][0]      # 첫 번째 태그 항목
    assert isinstance(first_tag_error, dict)
    assert ('pk' in first_tag_error) or ('non_field_errors' in first_tag_error)