from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.contrib.auth import update_session_auth_hash

from member.serializers.profile import UserPasswordUpdateSerializers, UserListSerializers
from permissions import ObjectIsRequestUser

__all__ = (
    'UserRetrieveUpdateDestroyView',
    'UserPasswordUpdateView',
)

User = get_user_model()


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    사용자 email, username, img_profile 변경
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializers
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        ObjectIsRequestUser,
    )

    def delete(self, request, *args, **kwargs):
        super().delete(self, request, *args, **kwargs)
        content = {
            "detail": "계정이 삭제되었습니다."
        }
        return Response(content, status=status.HTTP_202_ACCEPTED)


class UserPasswordUpdateView(generics.RetrieveUpdateAPIView):
    """
    사용자 비밀번호 변경
    """
    queryset = User.objects.all()
    serializer_class = UserPasswordUpdateSerializers
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        ObjectIsRequestUser,
    )

    def patch(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer = self.get_serializer(data=request.data)
            user_serializer = UserListSerializers(data=request.data)
            if not user.check_password(request.data.get('password')):
                raise serializer.ValidationError(
                    "기존 비밀번호가 일치하지 않습니다."
                )
            user.set_password(request.data.get('new_password2'))
            user.save()

            # make sure the user stays logged in
            update_session_auth_hash(request, request.user)
            content = {
                'detail': "비밀번호가 변경되었습니다.",
                'email': user.email,
                'password': user.password,
            }
            return Response(content, status=status.HTTP_200_OK)

        content = {
            "detail": "비밀번호 변경에 실패했습니다. 다시 시도해주세요.",
        }
        print('ended!!')
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
