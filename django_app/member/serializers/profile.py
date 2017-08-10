from django.contrib.auth import get_user_model
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
    """
    유저 정보(이메일 / 유저명 / 프로필이미지) 변경
    """

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
        ).split("?")[0]
        instance.save()
        return instance


class UserPasswordUpdateSerializers(serializers.ModelSerializer):
    """
    유저 비밀번호 변경 시리얼라이저
    """
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
            'password',
            'new_password1',
            'new_password2',
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
        password = attrs.get('password')
        new_password1 = attrs.get('new_password1')
        new_password2 = attrs.get('new_password2')
        if password:
            if not (password and new_password1 and new_password2):
                return serializers.ValidationError(
                    "필수 입력칸입니다."
                )
            elif new_password1 != new_password2:
                return serializers.ValidationError(
                    "새로운 비밀번호와 확인용 비밀번호가 일치하지 않습니다."
                )
            return attrs
