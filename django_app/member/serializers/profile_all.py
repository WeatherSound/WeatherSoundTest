from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

__all__ = (
    'UserListSerializers',
    'UserRetrieveUpdateDestroySerializers',
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
        )
        extra_kwargs = {
            'new_password1': {'write_only': True},
            'new_password2': {'write_only': True},
        }

    def validate(self, data):
        password = data.get('password')
        if data.get('new_password1') == '' and data.get('new_password2') == '':
            data.pop('password')
            data.pop('new_password1')
            data.pop('new_password2')
        elif data.get('new_password1') != data.get('new_password2'):
            return serializers.ValidationError(
                "새로운 비밀번호와 확인용 비밀번호가 일치하지 않습니다."
            )
        return data

    def update(self, instance, validated_data):
        print('instance.nick1;;;;', instance.nickname)
        # instance.nickname = validated_data.get(
        #     'nickname',
        #     instance.nickname
        # )
        print('instance.nick2;;;;', instance.nickname)
        # instance.img_profile = validated_data.get(
        #     'img_profile',
        #     instance.img_profile
        # )
        print('instance.img_profile;;;;', instance.nickname)
        instance.save()
        return instance
