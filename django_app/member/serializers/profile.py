from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

User = get_user_model()

__all__ = (
    'UserListSerializers',
    'UserRetrieveUpdateDestroySerializers',
    'UserPasswordUpdateSerializers',
)


class UserListSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk',
            'email',
            'username',
            'img_profile',
            'password',
            'is_active',
            'is_admin',
        )
        read_only = (
            'email',
        )
        write_only = (
            'password',
        )


class UserRetrieveUpdateDestroySerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk',
            'email',
            'username',
            'img_profile',
        )
        read_only = (
            'email',
        )

    def validate(self, attrs):
        pk = attrs.get('pk')
        if not pk:
            raise serializers.ValidationError(
                _('User doesn\'t exist')
            )
        return attrs

    def update(self, instance, validated_data):
        # get 예외처리?
        instance.email = validated_data.get(
            'email',
            instance.email,
        )
        instance.username = validated_data.get(
            'username',
            instance.username
        )
        instance.img_profile = validated_data.get(
            'img_profile',
            instance.img_profile
        )
        instance.save()
        return instance


class UserPasswordUpdateSerializers(serializers.ModelSerializer):
    password = serializers.CharField(
        label='password verify',
        max_length=50,
        write_only=True,
        style={'input_type': 'password'}
    )
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
            'new_password1',
            'new_password2',
        )
        read_only = (
            'email',
        )

    # def validate_password(self, password):
    #     if password:
    #         user = User.objects.filter(email=email)
    #         if password == user.password:
    #             return force_text(password)
    #     else:
    #         raise serializers.ValidationError(
    #             _("Enter the current password.")
    #         )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        new_password1 = attrs.get('new_password1')
        new_password2 = attrs.get('new_password2')
        if password:
            user = User.objects.filter(email=email)
            if self.authenticate(user.email, password):
                pass
            raise serializers.ValidationError(
                _('Password didn\'t match.')
            )

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
