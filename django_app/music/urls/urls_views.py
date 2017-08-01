from django.conf.urls import url

from music import views

app_name = 'music'
urlpatterns = [
    url(r'^$', views.MusicListView.as_view(), name='musiclist'),
]