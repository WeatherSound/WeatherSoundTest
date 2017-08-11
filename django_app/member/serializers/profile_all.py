from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

__all__ = (
    'UserListSerializers',
    'UserRetrieveUpdateDestroySerializers',
    # 'UserPasswordUpdateSerializers',
)


class UserListSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk',
            'username',
            'nickname',
            'img_profile',
            'password',
            'is_active',
            'is_admin',
        )
        read_only = (
            'username',
        )
        write_only = (
            'password',
        )


class UserRetrieveUpdateDestroySerializers(serializers.ModelSerializer):
    """
    유저 정보(이메일 / 유저명 / 프로필이미지 / 비밀번호) 변경
    """
    password = serializers.CharField(
        label='password verify',
        max_length=50,
        write_only=True,
        allow_blank=True,
        style={'input_type': 'password'}
    )
    new_password1 = serializers.CharField(
        label='new password',
        max_length=50,
        write_only=True,
        allow_blank=True,
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        label='confirm new password',
        max_length=50,
        write_only=True,
        allow_blank=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'username',
            'nickname',
            'img_profile',
            'password',
            'new_password1',
            'new_password2',
        )

    def validate(self, data):
        if data.get('password'):
            if not (data.get('new_password1') and data.get('new_password2')):
                return serializers.ValidationError(
                    "필수 입력칸입니다."
                )
            elif data.get('new_password2') != data.get('new_password2'):
                return serializers.ValidationError(
                    "새로운 비밀번호와 확인용 비밀번호가 일치하지 않습니다."
                )
            return data

    def update(self, instance, validated_data):
        if validated_data is not None:
            instance.nickname = validated_data.get(
                'nickname',
                instance.nickname
            )
            instance.img_profile = validated_data.get(
                'img_profile',
                instance.img_profile
            )
            if validated_data.get('password'):
                instance.password = validated_data.get(
                    'new_password2',
                    instance.password
                )

        instance.save()
        return instance
