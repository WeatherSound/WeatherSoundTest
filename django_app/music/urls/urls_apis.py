from django.conf.urls import url

from music import apis

urlpatterns = [
    url(r'^$',
        # apis.MusicListView.as_view(),
        apis.MainPlaylistListView.as_view(),
        name='musiclist',
        ),
    # url(r"^playlist/$",
    #     apis.PlaylistListCreateView.as_view(),
    #
    #     ),
    # url(r"^userplaylist/$",
    #     apis.UserPlaylistListCreateView.as_view(),
    #     name="playlist",
    #     ),
    url(r"^mainlist/$",
        apis.MainPlaylistListView.as_view(),
        name="mainlist"),
    url(r"^personallist/(?P<pk>\d+)/$",
        apis.UserMusiclistRetrieveUpdateDestroy.as_view(),
        name="PersonalMuiscList"
        )
    # url(r"^test/$", apis.PlaylistMusicsListCreateView.as_view(), name="test"),
]
