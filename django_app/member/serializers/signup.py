from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

User = get_user_model()

__all__ = (
    'UserSignupSerializers',
)


class UserSignupSerializers(serializers.ModelSerializer):
    password1 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'username',
            'nickname',
            'img_profile',
            'password1',
            'password2',
        )

    def validate(self, data):
        username = data.get('username')
        password1 = data.get('password1')
        password2 = data.get('password2')

        if User.objects.filter(username=username).exists():
            return serializers.ValidationError(
                "존재하는 이메일 계정입니다."
            )
        elif validate_email(username):
            raise serializers.ValidationError(
                "이메일 양식이 올바르지 않습니다."
            )
        elif password1 != password2:
            raise serializers.ValidationError(
                "입력하신 비밀번호와 확인용 비밀번호가 일치하지 않습니다."
            )
        return data

    def save(self):
        user = User.objects.create_user(
            username=self.validated_data.get('username'),
            nickname=self.validated_data.get('nickname'),
            password=self.validated_data.get('password2'),
            img_profile=self.validated_data.get('img_profile'),
            # TODO 계정활성화 메일 보낼 시 is_active는 False로 돌릴 것.
        )
        return user
