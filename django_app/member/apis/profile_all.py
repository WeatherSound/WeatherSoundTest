from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
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
        ObjectIsRequestUser,
        permissions.IsAuthenticated,
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

    def put(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        serializer_class = UserRetrieveUpdateDestroySerializers
        serializer = serializer_class(user, data=request.data, partial=True)

        # 비밀번호를 변경하지 않을 경우
        # if request.data.get('password') == '' or request.data.get('password') is None:
        # 변경할 비밀번호를 넣지 않은 경우 value='' or None 이므로 default값이 적용되는데
        if not request.data.get('password', default=None):
            serializer.is_valid(raise_exception=True)
            update_info = serializer.save()

            # 닉네임 저장(수정하지 않으면 본래값)
            # update_info.nickname = user.nickname if request.data.get(
            #     'nickname') == '' or request.data.get('nickname') is None else request.data.get('nickname')
            update_info.nickname = user.nickname if not request.data.get(
                'nickname', default=None) else request.data.get('nickname')
            update_info.save()

            # 프로필 이미지 저장(수정하지 않으면 본래값)
            # update_info.img_profile = user.img_profile if request.data.get(
            #     'img_profile') == '' or request.data.get('img_profile') is None else request.data.get('img_profile')
            update_info.img_profile = user.img_profile if not request.data.get(
                'img_profile', default=None) else request.data.get('img_profile')

            update_info.save()
            # 저장
            user_serializer = UserListSerializers(update_info, partial=True)
            content = {
                "datail": "회원정보가 변경되었습니다.",
                "userInfo": user_serializer.data,
            }
            return Response(
                content,
                status=status.HTTP_202_ACCEPTED
            )

        else:
            # 비밀번호를 변경하는 경우
            if request.data.get('password') is not None and user.check_password(request.data.get('password')):
                # 비밀번호가 맞는지 체크한다
                user.set_password(request.data.get('new_password2'))
                # 비번체크 통과했으므로 비밀번호를 새로 설정한다
                serializer.is_valid(raise_exception=True)
                update_info = serializer.save()

                # 닉네임 저장
                update_info.nickname = user.nickname if request.data.get(
                    'nickname') == '' or request.data.get('nickname') is None else request.data.get('nickname')
                update_info.save()

                # 프로필 이미지 저장
                update_info.img_profile = user.img_profile if request.data.get(
                    'img_profile') == '' or request.data.get('img_profile') is None else request.data.get('img_profile')
                print(user.password)
                print('유저 저장')

                user_serializer = UserListSerializers(update_info, partial=True)
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

    def delete(self, request, *args, **kwargs):
        content = {
            "detail": "계정이 삭제되었습니다."
        }
        super().destroy(self, request, *args, **kwargs)
        return Response(content, status=status.HTTP_202_ACCEPTED)
