import requests
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from config import settings
from member.serializers import UserListSerializers

__all__ = (
    'FacebookLoginAPIView',
    'TokenUserInfoAPIView',
)

User = get_user_model()


class TokenUserInfoAPIView(APIView):
    def post(self, request):
        token_string = request.data.get('token')
        try:
            token = Token.objects.get(key=token_string)
        except Token.DoesNotExist:
            raise APIException('token invalid')
        user = token.user
        user_serializer = UserListSerializers(user)
        content = {
            'token': token,
            'userInfo': user_serializer.data,
        }
        return Response(content, status=status.HTTP_202_ACCEPTED)


class FacebookLoginAPIView(APIView):
    FACEBOOK_APP_ID = settings.FACEBOOK_API_KEY
    FACEBOOK_SECRET_CODE = settings.FACEBOOK_API_SECRET_CODE
    # 앱 액세스토큰 생성
    APP_ACCESS_TOKEN = '{}|{}'.format(
        FACEBOOK_APP_ID,
        FACEBOOK_SECRET_CODE
    )

    def post(self, request):
        token = request.data.get('token')
        if not token:
            raise APIException({"detail": "액세스 토큰이 필요합니다."})

        # 프론트로부터 전달받은 token을 Facebook의 debug_token API를 이용해
        # 검증한 결과를 debug_result에 할당
        self.debug_token(token)
        user_info = self.get_user_info(token=token)
        # 이미 존재하면 가져오고 없으면 페이스북 유저 생성
        if User.objects.filter(username=user_info['id']).exists():
            user = User.objects.get(username=user_info['id'])
        # 모델 매니저를 통하여 페이스북 유저정보를 저장하고 유저 생성
        else:
            user = User.objects.get_or_create_facebook_user(user_info)

        # DRF 토큰을 생성
        token, token_created = Token.objects.get_or_create(user=user)
        user_serializer = UserListSerializers(user)

        # 관련정보를 한번에 리턴
        content = {
            'token': token.key,
            'userInfo': user_serializer.data,
        }
        return Response(content, status=status.HTTP_202_ACCEPTED)

    def debug_token(self, token):
        """
        주어진 token으로 Facebook API의 debug_token을 실행, 결과를 리턴
        :param token: 프론트엔드에서 유저가 페이스북 로그인 후 반환된
        authResponse 내의 access token 값
        :return: Facebook API의 debug_token 실행 후의 결과
        """
        # 디버그할 토큰을 보낼 url
        url_debug_token = "https://graph.facebook.com/debug_token"
        # 받아온 액세스토큰과 앱 아이디를 파라미터로 보내기 위해 딕셔너리에 넣어준다.
        url_debug_token_params = {
            'input_token': token,
            'access_token': self.APP_ACCESS_TOKEN,
        }
        # requests 모듈을 사용하여 response를 받아온다
        response = requests.get(url_debug_token, url_debug_token_params)
        # 받아온 response를 json 구조로 출력
        result = response.json()
        # 만약 응답에 에러가 있을 경우에는 API 예외처리를 해준다.
        if 'error' in result or 'error' in result['data']:
            raise APIException({"detail": "토큰이 유효하지 않습니다."})
        return result

    def get_user_info(self, token):
        """
        액세스 토큰을 사용하여 페이스북에 등록된 유저의 정보를 가져온다.
        """
        url_user_info = 'https://graph.facebook.com/v2.9/me'
        url_user_info_params = {
            'access_token': token,
            # 권한을 요청하지 않아도 오는 기본 정보
            # 반드시 scope 내용(받아올 정보)을 적어줘야한다.
            'fields': ','.join([
                'id',
                'name',
                'email',
                'first_name',
                'last_name',
                'picture.type(large)',
                'gender',
            ])
        }
        # 요청을 보내 response를 받는다.
        response = requests.get(url_user_info, params=url_user_info_params)
        result = response.json()
        return result

