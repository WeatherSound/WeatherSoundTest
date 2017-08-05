from django.contrib.auth import login as django_login
from eyed3.compat import unicode
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from member.serializers import CustomAuthTokenSerializers


class CustomAuthTokenView(APIView):
    """
    Anonymous user가 이메일 / 비밀번호를 입력하면
    그에 따른 토큰을 생성하여 전달해준다.
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)
    serializer_class = CustomAuthTokenSerializers

    def get(self, request, format=None):
        content = {
            'user': unicode(request.user),
            'auth': unicode(request.auth),
        }
        return Response(content,
                        status=status.HTTP_200_OK)

    def post(self, request, format=None, *args, **kwargs):
        """
        serializer를 통과해 유효한 user의 토큰값을 생성(없을경우) or 반환(있을 경우)
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        content = {
            'token': token.key,
            'email': user.email,
        }
        django_login(request, user)
        return Response(content,
                        status=status.HTTP_202_ACCEPTED)
