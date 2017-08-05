from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

User = get_user_model()

__all__ = (
    'UserSignupSerializers',

)


class UserSignupSerializers(serializers.Serializer):
    email_account = serializers.CharField(
        max_length=50
    )
    nickname = serializers.CharField(
        label="nickname",
        max_length=50
    )
    password1 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_email_account(self, email_account):
        if User.objects.filter(email=email_account).exists():
            raise serializers.ValidationError(
                _('Email already exists.')
            )
        elif validate_email(email_account):
            raise serializers.ValidationError(
                _('Please enter a proper email account.')
            )
        return email_account

    def validate_nickname(self, nickname):
        if User.objects.filter(username=nickname).exists():
            raise serializers.ValidationError(
                _('Nickname already exists.')
            )
        return nickname

    def validate(self, attrs):
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')
        if password1 != password2:
            raise serializers.ValidationError(
                _('Password did not match.')
            )
        return attrs

    def save(self):
        user = User.objects.create_user(
            email=self.validated_data.get('email_account'),
            username=self.validated_data.get('username'),
            password=self.validated_data.get('password1'),
            # TODO 계정활성화 메일 보낼 시 is_active는 False로 돌릴 것.
            is_active=True
        )
        return user