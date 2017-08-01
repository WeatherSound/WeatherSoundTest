from .base import *

config_secret_debug = json.loads(open(CONFIG_SECRET_DEBUG_FILE).read())

WSGI_APPLICATION = 'config.wsgi.debug.application'

# debug mode / allowed_hosts setting
DEBUG = True
ALLOWED_HOSTS = config_secret_debug['django']['allowed_hosts']

# debug 모드에서만 django_extensions 설치
INSTALLED_APPS.append('django_extensions')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(ROOT_DIR, '.static_root')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(ROOT_DIR, '.media')


# 서버 실행시 구별용 출력
print('@@@@@@@@@@ DEBUG: ', DEBUG)
print('@@@@@@@@@@ ALLOWED_HOSTS: ', ALLOWED_HOSTS)


# debug - sqlite3
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(ROOT_DIR, 'db.sqlite3'),
    }
}
