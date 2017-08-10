from django.contrib.auth import get_user_model, login as django_login
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from member.serializers import UserListSerializers, UserSignupSerializers
from member.tokens import account_activation_token

User = get_user_model()


__all__ = (
    'UserListView',
    'UserSignupView',
    'AccountActivationView',
)


class UserListView(generics.ListCreateAPIView):
    """
    기본 UserList 뷰
    """
    # TODO 개발 완료 후 IsAdminUser로 권한 변경하기
    permission_classes = (AllowAny,)
    queryset = User.objects.all().order_by('pk')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserListSerializers

    def pre_save(self, obj):
        if self.request.user.is_admin:
            obj.owner = self.request.user


class UserSignupView(generics.RetrieveUpdateAPIView):
    """
    GET 요청 : 유저 리스트 반환
    POST 요청 : 회원가입 시리얼라이저 반환, 회원가입 가능

    추후 POST 요청 추가작업 : 가입하면 is_active가 False이고 가입한 이메일로 보내진
    메일의 링크를 클릭하면 is_active=True가 반환된다. 이는 샐러리로 연동해야함!
    """
    permission_classes = (AllowAny,)
    queryset = User.objects.all().order_by('pk')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserListSerializers
        elif self.request.method == 'POST':
            return UserSignupSerializers

    def pre_save(self, obj):
        if self.request.user.is_admin:
            obj.owner = self.request.user

    def post(self, request, *args, **kwargs):
        serializer_class = UserSignupSerializers
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # img_profile에 새로운 파일을 올릴 경우에는 기본 파일을
        # 사용자가 넣은 파일로 바꿔주고 저장.
        if request.data.get('img_profile'):
            user.img_profile = request.data.get('img_profile')
            user.save()
        user_serializer = UserListSerializers(user)

        # TODO 계정 활성화 메일 보내기 + celery 나중에 도입..
        # email = serializer.validated_data['email']
        # user = User.objects.get(email=email)
        # current_site = get_current_site(request)
        # message = render_to_string('acc_activate_email.html', {
        #     'user': user,
        #     'domain': current_site.domain,
        #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        #     'token': account_activation_token.make_token(user),
        # })
        # mail_subject = 'Hello! Welcome to WeatherSound. Please activate your account.'
        # to_email = serializer.validated_data('email')
        # email = EmailMessage(mail_subject, message, to=[to_email])
        # email.send()
        # msg = 'Account activation email sent. Please check your email.'
        # super(UserListView, self).post(self, request, *args, **kwargs)
        content = {
            'result': serializer.data,
            'userInfo': user_serializer.data,
            # TODO 이메일계정활성화 기능 구현 후 user 정보 자체를 반환하기
        }
        return Response(
            content,
            status=status.HTTP_201_CREATED
        )


class AccountActivationView(APIView):
    @staticmethod
    def activate(request, uidb64, token):
        uid = force_text(urlsafe_base64_decode(uidb64))
        try:
            print('uid: ', uid)
            print('uidb64: ', uidb64)
            user = User.objects.get(pk=uid)
            print(user)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            django_login(request, user)
            content = {
                'user': user.email,
                'result': 'Successfully activated the account. Enjoy!',
            }
            return Response(
                content,
                status=status.HTTP_201_CREATED
            )
        content = {
            'detail': 'Activating account failed. Please try again.',
        }
        return Response(
            content,
            status=status.HTTP_401_UNAUTHORIZED
        )

    def get(self, request, format=None):
        uid = request.get('uidb64')
        token = request.get('token')
        self.activate(request, uid, token)
