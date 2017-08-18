import re

import requests
from django.contrib.auth import models as auth_models, get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager as DjangoUserManager, UserManager
from django.core.exceptions import ValidationError
from django.core.files.temp import NamedTemporaryFile
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from utils.fields import CustomImageField
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token

__all__ = (
    'MyUser',
)


class MyUserManager(BaseUserManager):
    def create_user(self, username, nickname, email=None, password=None, **extra_fields):
        try:
            user = self.model(
                user_type=User.USER_TYPE_DJANGO,
                username=self.normalize_email(username),
                nickname=nickname,
                email=email if email else ''
            )
            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('is_superuser', False)
            user.set_password(password)
            # TODO 계정 활성화 메일 작동 전에는 False
            user.is_active = True
            user.save()
            return user
        except ValidationError:
            raise ValidationError({"detail": "이메일 양식이 올바르지 않습니다."})

    def create_superuser(self, username, nickname, password=None, **extra_fields):
        try:
            user = self.create_user(
                user_type=User.USER_TYPE_DJANGO,
                username=username,
                nickname=nickname,
                password=password,
            )
            user.is_admin = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            return user
        except ValidationError:
            raise ValidationError("이메일 양식이 올바르지 않습니다.")

    def get_or_create_facebook_user(self, user_info):
        fb_user, user_created = self.get_or_create(
            user_type=User.USER_TYPE_FACEBOOK,
            username=user_info['id'],
            nickname=user_info['first_name'],
            email='',
        )

        if user_created and user_info.get('picture'):
            url_profile = user_info['picture']['data']['url']

            # 이미지 확장자를 가져오는 정규표현식
            p = re.compile(r'.*\.([^?]+)')
            img_ext = re.search(p, url_profile).group(1)
            img_name = '{}.{}'.format(
                fb_user.pk,
                img_ext
            )
            # 이미지 파일을 임시로 저장할 파일 객체를 할당
            temp_file = NamedTemporaryFile()
            # 이미지를 다운로드함
            response = requests.get(url_profile)
            # 임시 파일객체에 다운로드한 이미지를 기록
            temp_file.write(response.content)
            # 페이스북 유저의 이미지를 주어진 이름으로 저장
            fb_user.img_profile.save('fb_profile.jpg', temp_file)
            return fb_user


# 사용자 정보 모델
class MyUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_DJANGO = 'django'
    USER_TYPE_FACEBOOK = 'facebook'
    CHOICES_USER_TYPE = (
        (USER_TYPE_DJANGO, 'Django'),
        (USER_TYPE_FACEBOOK, 'Facebook'),
    )
    user_type = models.CharField(
        max_length=10,
        choices=CHOICES_USER_TYPE,
        default=USER_TYPE_DJANGO
    )
    username = models.CharField(
        _('email address'),
        max_length=100,
        unique=True,
        null=True,
    )
    nickname = models.CharField(
        _('nickname'),
        max_length=40,
        null=True,
    )
    # TODO img_profile - CustomImageField 설정 필요
    img_profile = CustomImageField(
        upload_to='member',
        blank=True,
        default='member/basic_profile.png'
    )
    email = models.EmailField(
        default='',
        null=True,
        blank=True,
    )
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(
        _('active'),
        default=True,
    )
    is_superuser = models.BooleanField(default=False)

    objects = MyUserManager()

    # Facebook user 생성용 매니저
    # objects_fb = FacebookUserManager()

    EMAIL_FIELD = 'username'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nickname', ]

    def __str__(self):
        return self.nickname if self.nickname else self.username

    @property
    def is_staff(self):
        """일반 사용자인지 아니면 스태프 권한이 있는지?"""
        return self.is_admin

    def email_user(self, subject, message, from_email=None):
        if validate_email(self.username):
            send_mail(subject, message, from_email, [self.username])
        return None

    def has_module_perms(self, app_label):
        """user가 주어진 app_label에 해당하는 권한이 있는지, has_perm과 비슷"""
        if self.is_active and self.is_superuser:
            return True
        return auth_models._user_has_module_perms(self, app_label)

    def has_perm(self, perm, obj=None):
        if self.is_active and self.is_superuser:
            return True

        return auth_models._user_has_perm(self, perm, obj)

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

User = get_user_model()


# 로그인시 유저의 인증 토큰을 생성하는 메서드.
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
