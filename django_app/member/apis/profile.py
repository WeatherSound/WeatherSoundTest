from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

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
        user_serializer = UserListSerializers(data=request.data)
        response_data = {}
        print(serializer)
        if serializer.is_valid():
            serializer = self.get_serializer(data=request.data)
            user_serializer = UserListSerializers(data=request.data)
            if not user.check_password(request.data.get('password')):
                raise ValidationError(
                    "기존 비밀번호가 일치하지 않습니다."
                )
            user.set_password(request.data.get('new_password2'))
            print('hello!!')
            user.save()
            response_data['UserInfo'] = user_serializer.data
            content = {
                'detail': "비밀번호가 변경되었습니다.",
                'UserInfo': response_data.values(),
            }
            return Response(content, status=status.HTTP_200_OK)
        response_data['UserInfo'] = user_serializer.data
        content = {
            "detail": "오류가 발생했습니다.",
            "UserInfo": response_data.values()
        }
        print('ended!!')
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # email = request.data['email']
        # password = request.data['password']
        # password2 = request.data['new_password2']
        # object = authenticate(
        #     request,
        #     username=email,
        #     password=password,
        # )
        # print(object)
        # if object is not None:
        #     user.set_password(password2)
        #     return user
        # else:
        #     msg = '기존 비밀번호가 일치하지 않습니다.'
        #     return Response(
        #         msg,
        #         status=status.HTTP_401_UNAUTHORIZED,
        #     )
