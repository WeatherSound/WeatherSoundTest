from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from utils.exception import SetCustomErrorMessagesMixin

User = get_user_model()

__all__ = (
    'CustomAuthTokenSerializers',

)


class CustomAuthTokenSerializers(SetCustomErrorMessagesMixin, serializers.ModelSerializer):
    """
    장고 기본 로그인에 필요한 이메일과 비밀번호를 받아
    rest 페이지에서 token값 및 이메일 값을 전달
    """
    username = serializers.CharField(
        max_length=50,
        help_text='example@example.com',
    )
    password = serializers.CharField(
        max_length=50,
        help_text='8자 이상 특수문자 포함 입력해주세요.',
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'pk',
            'username',
            'password',
        )
        read_only = (
            'username',
        )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username:
            if attrs['username'].errors:
                raise serializers.ValidationError({
                    "detail": "이메일을 입력하세요.",
                })

        elif validate_email(username):
            if attrs['username'].errors:
                raise serializers.ValidationError({
                    "detail": "유효한 이메일 계정이 아닙니다. 정확히 입력해주세요.",
                })

        if username and password:
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                if not user.is_active:
                    msg = '유저 계정이 비활성화된 상태입니다. 이메일을 확인하세요.'
                    raise serializers.ValidationError({
                        "detail": msg
                    })
            else:
                msg = '주어진 정보와 일치하는 계정정보가 없습니다.'
                raise serializers.ValidationError({
                    "detail": msg
                })
        else:
            msg = '이메일과 비밀번호를 입력해주세요.'
            raise serializers.ValidationError({
                "detail": msg
            })

        attrs['user'] = user
        return attrs
