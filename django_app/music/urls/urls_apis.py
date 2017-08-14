from django.conf.urls import url

from music import apis

urlpatterns = [
    url(r'^$',
        apis.MusicListView.as_view(),
        name='musiclist',
        ),
    url(r"^playlist/$",
        apis.PlaylistListCreateView.as_view(),
        
        ),
    url(r"^userplaylist/$",
        apis.UserPlaylistListCreateView.as_view(),
        name="playlist",
        ),
]
