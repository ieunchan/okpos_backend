from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from .models import Product, ProductOption, Tag


class ProductOptionSerializer(serializers.ModelSerializer):
    _delete = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = ProductOption
        fields = ['id', 'name', 'price', '_delete']
        extra_kwargs = {
            'id': {'read_only': False, 'required': False},
            'name': {'required': False},
            'price': {'required': False},
        }


class TagSerializer(serializers.ModelSerializer):
    # 입력 시 pk도 허용 (id로 매핑), 응답에는 id만 노출
    pk = serializers.IntegerField(source='id', required=False, write_only=True)

    class Meta:
        model = Tag
        fields = ['id', 'pk', 'name']
        extra_kwargs = {
            'id': {'read_only': False, 'required': False},
            'name': {'required': False, 'validators': []},
        }


class ProductSerializer(WritableNestedModelSerializer):
    option_set = ProductOptionSerializer(many=True, required=False)
    tag_set = TagSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'option_set', 'tag_set']

    def update(self, instance, validated_data):
        # nested 데이터 분리
        options_data = validated_data.pop('option_set', None)
        tags_data = validated_data.pop('tag_set', None)

        # 기본 필드 업데이트 (예: name)
        instance = super().update(instance, validated_data)

        # 옵션 삭제 처리 및 보존 리스트 구축
        remaining_options = None
        if isinstance(options_data, list):
            remaining_options = []
            for option_data in options_data:
                if option_data.pop('_delete', False):
                    option_id = option_data.get('id')
                    if option_id:
                        try:
                            opt = ProductOption.objects.get(id=option_id, product=instance)
                            opt.delete()
                        except ProductOption.DoesNotExist:
                            pass
                    # 삭제 항목은 remaining에 추가하지 않음
                    continue
                remaining_options.append(option_data)

        # drf-writable-nested로 나머지 upsert 수행
        nested_payload = {}
        if remaining_options is not None:
            nested_payload['option_set'] = remaining_options
        if isinstance(tags_data, list):
            nested_payload['tag_set'] = tags_data

        if nested_payload:
            return super().update(instance, nested_payload)
        return instance