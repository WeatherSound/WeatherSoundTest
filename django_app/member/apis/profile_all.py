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

    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        serializer_class = UserListSerializers
        serializer = serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        content = {
            'userInfo': serializer.data,
        }
        return Response(content, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        serializer_class = UserRetrieveUpdateDestroySerializers
        serializer = serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        update_info = serializer.save()
        print(update_info)
        if request.data.get('password'):
            print('비밀번호가 있다')
            if user.check_password(request.data.get('password')):
                print('비밀번호가 맞는지 체크한다')
                user.set_password(request.data.get('new_password2'))
                print(request.data.get('new_password2'))
                print('비번체크 통과했으므로 비밀번호를 새로 설정한다')
                update_info.nickname = request.data.get('nickname', update_info.nickname)
                update_info.img_profile = request.data.get('img_profile', update_info.img_profile)
                print(update_info)
                update_info.save()
                print('유저 저장')

                user_serializer = UserListSerializers(update_info, partial=True)

                print(user_serializer.data)
                content = {
                    'detail': "회원정보가 변경되었습니다. 재로그인해주세요.",
                    'userInfo': user_serializer.data,
                }
                return Response(content, status=status.HTTP_202_ACCEPTED)

            else:
                content = {
                    "detail": "기존 비밀번호가 일치하지 않습니다.",
                }
                print('비번 안맞아서 400 에러 발생')
                return Response(
                    content,
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            update_info.nickname = request.data.get('nickname', update_info.nickname)
            update_info.img_profile = request.data.get('img_profile', update_info.img_profile)
            update_info.save()
            user_serializer = UserListSerializers(update_info, partial=True)
            content = {
                "datail": "회원정보가 변경되었습니다.",
                "userInfo": user_serializer.data,
            }
            return Response(
                content,
                status=status.HTTP_202_ACCEPTED
            )

    def delete(self, request, *args, **kwargs):
        content = {
            "detail": "계정이 삭제되었습니다."
        }
        super().destroy(self, request, *args, **kwargs)
        return Response(content, status=status.HTTP_202_ACCEPTED)
