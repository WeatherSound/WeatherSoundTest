from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
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
    parser_classes = (
        MultiPartParser,
        FormParser,)  # add
    permission_classes = (
        ObjectIsRequestUser,
        permissions.IsAuthenticated,
    )

    def get(self, request, *args, **kwargs):
        # url의 pk값으로 User 객체를 user에 할당
        user = User.objects.get(pk=kwargs['pk'])
        serializer_class = UserListSerializers
        serializer = serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # 시리얼라이저의 데이터를 json형태로 출력
        content = {
            'userInfo': serializer.data,
        }
        return Response(content, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        serializer_class = UserRetrieveUpdateDestroySerializers
        serializer = serializer_class(user, data=request.data, partial=True)
        parser_classes = (MultiPartParser, FormParser,)  # 추가

        # (1) 비밀번호가 다 있을 경우
        if request.data.get('password', default=None) and request.data.get(
                'new_password1', None) and request.data.get('new_password2', None):
            if user.check_password(request.data.get('password')):
                # 비번체크 통과했으므로 비밀번호를 새로 설정한다
                user.set_password(request.data.get('new_password2'))
                serializer.is_valid(raise_exception=True)
                update_info = serializer.save()

                # 닉네임 저장(수정하지 않으면 본래값)
                update_info.nickname = user.nickname if not request.data.get(
                    'nickname', default=None) else request.data.get('nickname')
                update_info.save()

                # 프로필 이미지 저장(수정하지 않으면 본래값)
                update_info.img_profile = user.img_profile if not request.data.get(
                    'img_profile', default=None) else request.data.get('img_profile')
                # 유저 저장

                user_serializer = UserListSerializers(update_info, partial=True)
                content = {
                    'detail': "회원정보가 변경되었습니다. 재로그인해주세요.",
                    'userInfo': user_serializer.data,
                }
                return Response(content, status=status.HTTP_202_ACCEPTED)
            # 기존 비밀번호가 일치하지 않는 경우 - 400 예외처리
            else:
                content = {
                    "detail": "기존 비밀번호가 일치하지 않습니다.",
                }
                # 비번 안맞아서 400 에러 발생
                return Response(
                    content,
                    status=status.HTTP_400_BAD_REQUEST
                )

        # (2) 비밀번호 파람을 입력했는데 이중 하나라도 없는 경우
        elif request.data.get('password', default=None) or request.data.get(
                'new_password1', None) or request.data.get('new_password2', None):
            content = {
                "detail": "비밀번호를 변경하시려면 필드를 모두 입력해주십시오."
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # (3) 비밀번호 값이 하나도 없을 경우(닉네임과 이미지만 변경하는 경우)
        else:
            serializer.is_valid(raise_exception=True)
            update_info = serializer.save()

            # 닉네임 저장(수정하지 않으면 본래값)
            # update_info.nickname = user.nickname if request.data.get(
            #     'nickname') == '' or request.data.get('nickname') is None else request.data.get('nickname')
            update_info.nickname = user.nickname if not request.data.get(
                'nickname', default=None) else request.data.get('nickname')
            update_info.save()

            # 프로필 이미지 저장(수정하지 않으면 본래값)
            update_info.img_profile = user.img_profile if not request.data.get(
                'img_profile', default=None) else request.data.get('img_profile')

            # 저장
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
        # 삭제 후 response를 오버라이드하여 메세지 보냄
        # if request.user.user_type == User.USER_TYPE_FACEBOOK:
        #     request.user.auth_token.delete()
        #     request.user.delete()
        #     content = {
        #         "detail": "소셜 계정이 삭제되었습니다."
        #     }
        #     return Response(content, status=status.HTTP_202_ACCEPTED)
        content = {
            "detail": "계정이 삭제되었습니다."
        }
        super().destroy(self, request, *args, **kwargs)
        return Response(content, status=status.HTTP_202_ACCEPTED)

