from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.admin import TokenAdmin

from music.models import Playlist, PlaylistMusics
from .forms import UserChangeForm, UserCreateForm
from .models import MyUser


class MyUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreateForm
    fieldsets = (
        (None, {'fields': ('email', 'username', 'img_profile', 'password')}),
        (_('Personal info'), {'fields': ('email',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_admin', 'is_superuser')}),
    )

    # User 생성시 필요한 필드셋 정의
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'img_profile', 'password1', 'password2'),
        }),
    )

    list_display = ('email', 'username', 'img_profile', 'is_admin', 'is_active')
    list_filter = ('is_admin',)
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ('user_permissions',)


# Admin - Token 페이지에 user 정보 표시
TokenAdmin.raw_id_fields = ('user',)

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Playlist)
admin.site.register(PlaylistMusics)
