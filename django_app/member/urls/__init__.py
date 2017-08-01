from django.conf.urls import url, include

from . import urls_views
from . import urls_apis

urlpatterns = [
    url(r'', include(urls_views)),
    url(r'^api/', include(urls_apis)),
    # rest api 로그인용 url
    url(r'^api-auth/', include('rest-framework.urls',
                               namespace='rest_framework')),

]