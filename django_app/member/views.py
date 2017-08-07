from django.contrib.auth import get_user_model, login as django_login, logout as django_logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from member.forms import SignupForm, LoginForm
from member.tokens import account_activation_token

User = get_user_model()


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.create_user()
            current_site = get_current_site(request)
            message = render_to_string('acc_activate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = 'Hello! Welcome to WeatherSound. Please activate your account.'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print('uid: ', uid)
        print('uidb64: ', uidb64)
        user = User.objects.get(pk=uid)
        print(user)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        print(token)
        user.is_active = True
        user.save()
        django_login(request, user)
        return HttpResponse('Thanks for confirmation. Now you can login to WeatherSound')
    else:
        print(uidb64)
        print(user)
        return HttpResponse('Activation link is invalid. Please try again.')


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            django_login(request, user)
        return redirect('music:musiclist')
    form = LoginForm()
    context = {
        'form': form,
    }
    return render(request, 'login.html', context)


def logout(request):
    django_logout(request)
    return redirect('member:login')
