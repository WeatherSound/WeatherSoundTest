from django.contrib.auth import get_user_model, logout as django_logout, login as django_login, authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import CustomAuthTokenSerializers, UserListSerializers

User = get_user_model()

__all__ = (
    'CustomAuthTokenView',
    'UserLogoutView',
)


class CustomAuthTokenView(APIView):
    """
    Anonymous user가 이메일 / 비밀번호를 입력하면
    그에 따른 토큰을 생성하여 전달해준다.
    """
    authentication_classes = (TokenAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)
    serializer_class = CustomAuthTokenSerializers

    # def get(self, request, format=None):
    #     content = {
    #         'user': unicode(request.user),
    #         'auth': unicode(request.auth),
    #     }
    #     return Response(
    #         content,
    #         status=status.HTTP_200_OK
    #     )

    def post(self, request, format=None, *args, **kwargs):
        """
        serializer를 통과해 유효한 user의 토큰값을 생성(없을 경우) or 반환(있을 경우)
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if authenticate(
                username=request.data.get('username'),
                password=request.data.get('password')
        ):
            token, created = Token.objects.get_or_create(user=user)
            user_serializer = UserListSerializers(user)
            content = {
                'token': token.key,
                'userInfo': user_serializer.data,
            }
            django_login(request, user)
            return Response(
                content,
                status=status.HTTP_202_ACCEPTED
            )
        else:
            content = {
                "detail": "아이디 또는 비밀번호가 일치하지 않습니다.",
            }
            return Response(
                content,
                status=status.HTTP_400_BAD_REQUEST
            )


class UserLogoutView(APIView):
    """
    유저의 토큰을 삭제하여 로그아웃시킴
    """
    permission_classes = (IsAuthenticated,)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (ObjectDoesNotExist, AttributeError):
            content = {
                "detail": _("No token given."),
            }
            django_logout(request)
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)
        # TODO 삭제할 토큰이 없을 경우 그대로 로그아웃 진행시켜야하는가?
        django_logout(request)
        content = {
            "detail": _("Successfully logged out."),
        }
        return Response(content, status=status.HTTP_200_OK)

    def get(self, request):
        return self.logout(request)
