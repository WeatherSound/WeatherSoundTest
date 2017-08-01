from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm


User = get_user_model()


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'img_profile',
            "nickname",
            'password1',
            'password2',
            # 'is_active',
            # 'is_admin',
        )

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
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
            'email',
            'img_profile',
            'password',
            "nickname",
            # 'is_active',
            # 'is_admin',
        )

    def clean_password(self):
        return self.initial["password"]


class SignupForm(forms.Form):
    """
    회원가입
    """
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'example@example.com',
            }
        )
    )
    nickname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': '유일해야 합니다.'
            }
        )
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

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if nickname and User.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError(
                'Nickname already exists'
            )
        return nickname

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        # password1과 password2가 존재하고 같지 않을 때
        if password1 and password2 and password2 != password1:
            raise forms.ValidationError(
                "Password2 should be identical to Password1."
            )
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email account is already in use."
            )
        return email

    def create_user(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password1']
        nickname = self.cleaned_data['nickname']
        user = User.objects.create_user(
            email=email,
            nickname=nickname,
            password=password,
            is_active=False,
        )
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'placeholder': '가입한 이메일계정을 입력하세요.',
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder': '비밀번호를 입력하세요.',
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('email')
        password = cleaned_data.get('password')
        is_active = cleaned_data.get('is_active')
        user = authenticate(
            username=username,
            password=password,
        )
        if user is not None:
            self.cleaned_data['user'] = user
        elif not is_active:
            raise forms.ValidationError(
                'Please confirm your email to activate the account.'
            )
        else:
            raise forms.ValidationError(
                'Login credentials not valid'
            )
        return self.cleaned_data
