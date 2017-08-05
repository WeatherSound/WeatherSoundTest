from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _


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


class UserPasswordUpdateSerializers(serializers.ModelSerializer):
    new_password1 = serializers.CharField(
        label='new password',
        max_length=50,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        label='confirm new password',
        max_length=50,
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'email',
            'password',
        )
        read_only_fields = (
            'email'
        )

    def validate_password(self, password):
        if password:
            user = User.objects.filter(email=self.email)
            if password == user.password:
                return password
        else:
            raise serializers.ValidationError(
                _("Enter the current password.")
            )

    def validate(self, attrs):
        new_password1 = attrs.get('new_password1')
        new_password2 = attrs.get('new_password2')
        if new_password1 and new_password2:
            if new_password1 == new_password2:
                User.objects.set_password(new_password2)
                return new_password2
            else:
                raise serializers.ValidationError(
                    _("Enter the identical password.")
                )
        else:
            raise serializers.ValidationError(
                _("Enter the new password.")
            )
