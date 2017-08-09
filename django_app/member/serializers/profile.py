from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
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
            'email',
            'username',
            'img_profile',
        )
        read_only = (
            'email',
        )

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
        print(password)
        new_password1 = attrs.get('new_password1')
        print(new_password1)
        new_password2 = attrs.get('new_password2')
        print(new_password2)
        if password:
            user = get_object_or_404(User, email=email)
            if not user.check_password(password):
                return serializers.ValidationError(
                    "기존 비밀번호가 일치하지 않습니다."
                )
            elif not (new_password1 and new_password2):
                return serializers.ValidationError(
                    "필수 입력칸입니다."
                )
            elif new_password1 != new_password2:
                return serializers.ValidationError(
                    "새로운 비밀번호와 확인용 비밀번호가 일치하지 않습니다."
                )
            return attrs
