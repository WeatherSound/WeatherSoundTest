from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from config import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^music/', include('music.urls.urls_views')),
]

urlpatterns += static(
    prefix=settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)