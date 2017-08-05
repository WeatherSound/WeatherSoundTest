from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

__all__ = (
    'UserListSerializers',
)


class UserListSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'img_profile',
            'password',
            'is_active',
            'is_admin',
        )
