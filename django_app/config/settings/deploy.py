from .base import *

config_secret_debug = json.loads(open(CONFIG_SECRET_DEBUG_FILE).read())

WSGI_APPLICATION = 'config.wsgi.debug.application'


# DEBUG = False  == Bad Request
# 자세한 오류내용을 보려면 'DEBUG = True' 설정
DEBUG = False
ALLOWED_HOSTS = config_secret_deploy['django']['allowed_hosts']


# Database
DATABASES = config_secret_deploy['django']['database']


### AWS settings ###
AWS_ACCESS_KEY_ID = config_secret_deploy['aws']['access_key_id']
AWS_SECRET_ACCESS_KEY = config_secret_deploy['aws']['secret_access_key']
AWS_STORAGE_BUCKET_NAME = config_secret_deploy['aws']['s3_bucket_name']
AWS_S3_REGION_NAME = config_secret_deploy['aws']['s3_region']
# AWS_S3_SIGNATURE_VERSION = config_secret_deploy['aws']['s3_signature_version']
S3_USE_SIGV4 = True


### Storage settings ###
STATICFILES_LOCATION = 'static'
MEDIAFILES_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'config.storages.MediaStorage'
STATICFILES_STORAGE = 'config.storages.StaticStorage'

# Statics URLs - 재정의
STATIC_URL = '/static/'
# TODO ebextensions으로 static file upload
STATIC_ROOT = os.path.join(ROOT_DIR, '.static_root')

# Media URLs - 재정의
MEDIA_URL = '/media/'
# TODO ebextensions으로 media file upload
MEDIA_ROOT = os.path.join(ROOT_DIR, '.media')


# 서버 실행시 구별용 출력
print('@@@@@@@@@@ DEBUG: ', DEBUG)
print('@@@@@@@@@@ ALLOWED_HOSTS: ', ALLOWED_HOSTS)

