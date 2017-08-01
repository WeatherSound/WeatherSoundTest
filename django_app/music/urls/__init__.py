from django.conf.urls import url
from .. import apis

urlpatterns = [
    url(r'^$', apis.MusicListCreateView.as_view(), name='musiclist'),
]