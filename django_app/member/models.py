from django.contrib.auth import models as auth_models, get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import models
from django.utils.translation import ugettext_lazy as _


__all__ = (
    'MyUser',
)


class MyUserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None, **extra_fields):
        try:
            validate_email(email)
            user = self.model(
                email=self.normalize_email(email),
                nickname=nickname,
            )
            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('is_superuser', False)
            user.set_password(password)
            user.is_active = False
            user.save()
            return user
        except ValidationError:
            raise ValidationError('이메일 양식이 올바르지 않습니다.')

    def create_superuser(self, email, nickname, password=None, **extra_fields):
        try:
            validate_email(email)
            user = self.create_user(
                email=email,
                nickname=nickname,
                # name=name,
                password=password,
            )
            user.is_admin = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            return user
        except ValidationError:
            raise ValidationError('이메일 양식이 올바르지 않습니다.')


# 사용자 정보 모델
class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        _('email address'),
        max_length=255,
        unique=True,
        null=True,
    )
    nickname = models.CharField(_('nickname'), max_length=40, null=True, unique=True)
    # TODO img_profile - CustomImageField 설정 필요
    img_profile = models.ImageField(upload_to='member', blank=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_superuser = models.BooleanField(default=False)
    # name = models.CharField(max_length=100, default="")

    objects = MyUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname', ]

    def __str__(self):
        return "nickname: {}".format(self.nickname if self.nickname else self.email)

    @property
    def is_staff(self):
        """일반 사용자인지 아니면 스태프 권한이 있는지?"""
        return self.is_admin

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

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
        return self.email if self.email else self.nickname

    def get_short_name(self):
        return self.email if self.email else self.nickname
