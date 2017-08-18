from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from member.serializers.profile import UserListSerializers1, UserPasswordUpdateSerializers1
from permissions import ObjectIsRequestUser

__all__ = (
    'UserRetrieveUpdateDestroyView1',
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
        if serializer.is_valid():
            serializer = self.get_serializer(data=request.data)
            user_serializer = UserListSerializers1(data=request.data)
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
                'userInfo': user_serializer.data,
            }
            return Response(content, status=status.HTTP_200_OK)

        content = {
            "detail": "비밀번호 변경에 실패했습니다. 다시 시도해주세요.",
        }
        print('ended!!')
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

# TODO 통합변경 코드 삭제
# def put(self, request, *args, **kwargs):
    #     user = User.objects.get(pk=kwargs['pk'])
    #     serializer_class = UserRetrieveUpdateDestroySerializers
    #     serializer = serializer_class(user, data=request.data, partial=True)
    #
    #     # 비밀번호를 변경하지 않을 경우
    #     # if request.data.get('password') == '' or request.data.get('password') is None:
    #     # 변경할 비밀번호를 넣지 않은 경우 value='' or None 이므로 default를 따른다
    #     # 이경우 not None == True 이므로 비밀번호가 없을 때 실행된다.
    #     if not (request.data.get('password', default=None) and request.data.get(
    #             'new_password1', None) and request.data.get('new_password2', None)):
    #         serializer.is_valid(raise_exception=True)
    #         update_info = serializer.save()
    #
    #         # 닉네임 저장(수정하지 않으면 본래값)
    #         # update_info.nickname = user.nickname if request.data.get(
    #         #     'nickname') == '' or request.data.get('nickname') is None else request.data.get('nickname')
    #         update_info.nickname = user.nickname if not request.data.get(
    #             'nickname', default=None) else request.data.get('nickname')
    #         update_info.save()
    #
    #         # 프로필 이미지 저장(수정하지 않으면 본래값)
    #         # update_info.img_profile = user.img_profile if request.data.get(
    #         #     'img_profile') == '' or request.data.get('img_profile') is None else request.data.get('img_profile')
    #         update_info.img_profile = user.img_profile if not request.data.get(
    #             'img_profile', default=None) else request.data.get('img_profile')
    #         update_info.save()
    #         # 저장
    #
    #         user_serializer = UserListSerializers(update_info, partial=True)
    #         content = {
    #             "datail": "회원정보가 변경되었습니다.",
    #             "userInfo": user_serializer.data,
    #         }
    #         return Response(
    #             content,
    #             status=status.HTTP_202_ACCEPTED
    #         )
    #
    #     # 비밀번호를 변경하는 경우
    #     else:
    #         # 비밀번호는 있으나 새로운 비밀번호와 확인용 비밀번호를 넣지 않았을 경우
    #         if request.data.get('password') is not None and not (request.data.get(
    #                 'new_password1', None) or request.data.get('new_password2', None)):
    #             content = {
    #                 "detail": "비밀번호를 변경하시려면 새 비밀번호와 확인용 비밀번호를 입력해 주세요."
    #             }
    #             return Response(content, status=status.HTTP_400_BAD_REQUEST)
    #
    #         # 모든 파라미터를 전달받을 경우 비밀번호가 맞는지 체크
    #         elif user.check_password(request.data.get('password')):
    #             # 비번체크 통과했으므로 비밀번호를 새로 설정한다
    #             user.set_password(request.data.get('new_password2'))
    #             serializer.is_valid(raise_exception=True)
    #             update_info = serializer.save()
    #
    #             # 닉네임 저장
    #             update_info.nickname = user.nickname if request.data.get(
    #                 'nickname') == '' or request.data.get('nickname') is None else request.data.get('nickname')
    #             update_info.save()
    #
    #             # 프로필 이미지 저장
    #             update_info.img_profile = user.img_profile if request.data.get(
    #                 'img_profile') == '' or request.data.get('img_profile') is None else request.data.get('img_profile')
    #             print(user.password)
    #             print('유저 저장')
    #
    #             user_serializer = UserListSerializers(update_info, partial=True)
    #             content = {
    #                 'detail': "회원정보가 변경되었습니다. 재로그인해주세요.",
    #                 'userInfo': user_serializer.data,
    #             }
    #             return Response(content, status=status.HTTP_202_ACCEPTED)
    #         else:
    #             content = {
    #                 "detail": "기존 비밀번호가 일치하지 않습니다.",
    #             }
    #             print('비번 안맞아서 400 에러 발생')
    #             return Response(
    #                 content,
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
