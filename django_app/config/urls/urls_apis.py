from django.conf.urls import url, include

urlpatterns = [
    url(r'^music/', include('music.urls.urls_apis')),
    url(r'^member/', include('member.urls.urls_apis')),
]