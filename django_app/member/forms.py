from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm


User = get_user_model()


class UserCreateForm(UserCreationForm):
    username = forms.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'nickname',
            'img_profile',
            'password1',
            'password2',
            # 'is_active',
            # 'is_admin',
        )

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.username = self.cleaned_data['username']
        if commit:
            user.is_active = False
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    User 업데이트 폼
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            'username',
            'nickname',
            'img_profile',
            'password',
            # 'is_active',
            # 'is_admin',
        )

    def clean_password(self):
        return self.initial["password"]


class SignupForm(forms.Form):
    """
    회원가입
    """
    username = forms.CharField(
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'example@example.com',
            }
        )
    )
    nickname = forms.CharField(
        widget=forms.TextInput()
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '특수문자 포함 10~12자리',
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '특수문자 포함 10~12자리',
            }
        )
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        # password1과 password2가 존재하고 같지 않을 때
        if password1 and password2 and password2 != password1:
            raise forms.ValidationError(
                "Password2 should be identical to Password1."
            )
        return password2

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This email account is already in use."
            )
        return username

    def create_user(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password1']
        nickname = self.cleaned_data['nickname']
        user = User.objects.create_user(
            username=username,
            nickname=nickname,
            password=password,
            is_active=False,
        )
        return user


# class LoginForm(forms.Form):
#     email = forms.EmailField(
#         widget=forms.EmailInput(
#             attrs={
#                 'placeholder': '가입한 이메일계정을 입력하세요.',
#             }
#         )
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={'placeholder': '비밀번호를 입력하세요.',
#             }
#         )
#     )
#
#     def clean(self):
#         cleaned_data = super().clean()
#         username = cleaned_data.get('email')
#         password = cleaned_data.get('password')
#         is_active = cleaned_data.get('is_active')
#         user = authenticate(
#             username=username,
#             password=password,
#         )
#         if user is not None:
#             self.cleaned_data['user'] = user
#         elif not is_active:
#             raise forms.ValidationError(
#                 'Please confirm your email to activate the account.'
#             )
#         else:
#             raise forms.ValidationError(
#                 'Login credentials not valid'
#             )
#         return self.cleaned_data
