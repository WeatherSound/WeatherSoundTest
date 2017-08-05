from django.conf.urls import url, include

from . import urls_views
from . import urls_apis

urlpatterns = [
    url(r'', include(urls_views)),

    # api/ 페이지를 모두 포함.
    url(r'^api/', include(urls_apis, namespace='rest_framework')),
]