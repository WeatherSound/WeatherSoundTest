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
    유저 정보(username / 프로필이미지 / 비밀번호) 변경
    """
    password = serializers.CharField(
        label='password verify',
        style={'input_type': 'password'},
        max_length=50,
        allow_blank=True,
    )
    new_password1 = serializers.CharField(
        label='new password',
        style={'input_type': 'password'},
        max_length=50,
        allow_blank=True,
    )
    new_password2 = serializers.CharField(
        label='confirm new password',
        style={'input_type': 'password'},
        max_length=50,
        allow_blank=True,
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
        read_only_fields = (
            'username',
            'new_password1',
            'new_password2',
        )


    def validate(self, data):
        if data.get('password'):
            if not (data.get('new_password1') and data.get('new_password2')):
                return serializers.ValidationError(
                    "필수 입력 필드입니다."
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

        instance.save()
        return instance
