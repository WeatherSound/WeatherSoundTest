from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response
from member.serializers.profile_all import UserListSerializers, \
    UserRetrieveUpdateDestroySerializers
from permissions import ObjectIsRequestUser

__all__ = (
    'UserRetrieveUpdateDestroyView',
    # 'UserPasswordUpdateView',
)

User = get_user_model()


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    사용자 username, nickname, img_profile, password 변경
    """
    queryset = User.objects.all()
    serializer_class = UserRetrieveUpdateDestroySerializers
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        ObjectIsRequestUser,
    )

    def patch(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        print(11111132132131293212321321312)
        if request.data.get('password'):
            if not user.check_password(request.data.get('password')):
                content = {
                    "detail": "기존 비밀번호가 일치하지 않습니다.",
                }
                return Response(
                    content,
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                user.set_password(request.data.get('new_password2'))
                user.save()
                print(343434)
                serializer = self.get_serializer(data=request.data)
                print(serializer)
                print(222222825383905832948320948320)

                if serializer.is_valid(raise_exception=True):
                    return serializer.validated_data
                print(serializer.validated_data)
                    # serializer = self.serializer_class(user, data=request.data)

                serializer.save()
                user_serializer = UserListSerializers(user)
                user_serializer.is_valid(raise_exception=True)

                content = {
                    'detail': "회원정보가 변경되었습니다. 재로그인해주세요.",
                    'updateInfo': serializer.data,
                    'userInfo': user_serializer.data,
                }
                return Response(content, status=status.HTTP_200_OK)
        else:
            serializer = self.serializer_class(user, data=request.data)
            print(555555555555555555555555555555)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user_serializer = UserListSerializers(data=request.data)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
            content = {
                "detail": "회원정보가 변경되었습니다.",
                "updateInfo": serializer.data,
                "userInfo": user_serializer.data,
            }
            print('ended!!')
            return Response(content, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        content = {
            "detail": "계정이 삭제되었습니다."
        }
        super().destroy(self, request, *args, **kwargs)
        return Response(content, status=status.HTTP_202_ACCEPTED)


# class UserPasswordUpdateView(generics.RetrieveUpdateAPIView):
#     """
#     사용자 비밀번호 변경
#     """
#     queryset = User.objects.all()
#     serializer_class = UserPasswordUpdateSerializers
#     permission_classes = (
#         permissions.IsAuthenticatedOrReadOnly,
#         ObjectIsRequestUser,
#     )

