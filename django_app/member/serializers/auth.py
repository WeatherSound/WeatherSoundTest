from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from rest_framework import serializers

User = get_user_model()

__all__ = (
    'CustomAuthTokenSerializers',

)


class CustomAuthTokenSerializers(serializers.Serializer):
    """
    장고 기본 로그인에 필요한 이메일과 비밀번호를 받아
    rest 페이지에서 token값 및 이메일 값을 전달
    """
    email_account = serializers.CharField(
        max_length=50,
    )
    password = serializers.CharField(
        max_length=50,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        email_account = attrs.get('email_account')
        password = attrs.get('password')

        if not email_account:
            raise serializers.ValidationError(
                "이메일을 입력하세요."
            )
        elif validate_email(email_account):
            raise serializers.ValidationError(
                "유효한 이메일 계정이 아닙니다 정확히 입력해주세요."
            )

        if email_account and password:
            if User.objects.filter(email=email_account).exists():
                user = User.objects.get(email=email_account)
                if not user.is_active:
                    msg = '유저 계정이 비활성화된 상태입니다. 이메일을 확인하세요.'
                    raise serializers.ValidationError(msg)
            else:
                msg = '주어진 정보와 일치하는 계정정보가 없습니다.'
                raise serializers.ValidationError(msg)
        else:
            msg = '이메일과 비밀번호를 입력해주세요.'
            raise serializers.ValidationError(msg)

        attrs['user'] = user
        return attrs