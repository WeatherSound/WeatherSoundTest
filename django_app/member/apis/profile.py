from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from member.serializers.profile import UserListSerializers1, UserPasswordUpdateSerializers1
from permissions import ObjectIsRequestUser

__all__ = (
    'UserRetrieveUpdateDestroyView1',
    'UserRetrieveUpdateDestroyViewTest',
    'UserPasswordUpdateView1',
)

User = get_user_model()


class UserRetrieveUpdateDestroyView1(generics.RetrieveUpdateDestroyAPIView):
    """
    사용자 username, img_profile 변경
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializers1
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


class UserRetrieveUpdateDestroyViewTest(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializers1
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        ObjectIsRequestUser,
    )


class UserPasswordUpdateView1(generics.RetrieveUpdateAPIView):
    """
    사용자 비밀번호 변경
    """
    queryset = User.objects.all()
    serializer_class = UserPasswordUpdateSerializers1
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        ObjectIsRequestUser,
    )

    def patch(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        serializer = self.get_serializer(data=request.data)
        print(1111111111111111111111111)
        if serializer.is_valid():
            print(222222222222222222222222)
            serializer = self.get_serializer(data=request.data)
            print(333333333333333333333333)
            user_serializer = UserListSerializers1(data=request.data)
            if not user.check_password(request.data.get('password')):
                raise serializer.ValidationError(
                    "기존 비밀번호가 일치하지 않습니다."
                )
            user.set_password(request.data.get('new_password2'))
            user.save()

            # make sure the user stays logged in
            update_session_auth_hash(request, request.user)
            print(44444444444444444444444444)
            content = {
                'detail': "비밀번호가 변경되었습니다.",
                'userInfo': user_serializer.data,
            }
            print(333333333333333333333333)
            return Response(content, status=status.HTTP_200_OK)

        content = {
            "detail": "비밀번호 변경에 실패했습니다. 다시 시도해주세요.",
        }
        print('ended!!')
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
