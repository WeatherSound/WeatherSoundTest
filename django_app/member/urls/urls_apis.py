from django.conf.urls import url

from member import apis
from music.apis import music

urlpatterns = [

    url(r'^(?P<pk>\d+)/$',
        apis.UserRetrieveUpdateDestroyView.as_view(),
        name='userinfo'
        ),
    url(r'^profile/(?P<pk>\d+)/$',
        apis.UserRetrieveUpdateDestroyView.as_view(),
        name='user_profile'
        ),
    url(r'^profile/(?P<pk>\d+)/edit/$',
        apis.UserRetrieveUpdateDestroyView.as_view(),
        name='userinfo_update'
        ),
    url(r'signup/$',
        apis.UserSignupView.as_view(),
        name='signup'
        ),
    url(r'^login/$',
        apis.CustomAuthTokenView.as_view(),
        name='login'
        ),
    url(r'^facebook-login/$',
        apis.FacebookLoginAPIView.as_view(),
        name='facebook_login'
        ),
    url(r'^token-user-info/',
        apis.TokenUserInfoAPIView.as_view(),
        name='fb_user_token'
        ),
    url(r'^logout/$',
        apis.UserLogoutView.as_view(),
        name='logout'
        ),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        apis.AccountActivationView.as_view(),
        name='activate'),
    ##############
    # Music urls #
    ##############
    url(r"^(?P<pk>\d+)/playlists/$",
        music.UserMusiclistRetrieveUpdateDestroy.as_view(),
        name="playlists"),
    url(r"^(?P<pk>\d+)/playlists/(?P<playlist_pk>\d+)/$",
        music.UserPlayListMusicsRetrieveDestroy.as_view(),
        name="playlist_detail",
        ),

    url(r'^$',
        apis.UserListView.as_view(),
        name='userlist'
        ),
]
