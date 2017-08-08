from django.conf.urls import url, include
from django.conf.urls.static import static

from config import settings
from . import urls_views
from . import urls_apis

urlpatterns = [
    url(r'', include(urls_views)),

    # api/ 페이지를 모두 포함.
    url(r'^api/', include(urls_apis, namespace='rest_framework')),
]

urlpatterns += static(
    prefix=settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)
