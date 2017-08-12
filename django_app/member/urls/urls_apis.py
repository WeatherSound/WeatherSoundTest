from django.conf.urls import url
from member import views, apis

urlpatterns = [
    url(r'^$',
        apis.UserListView.as_view(),
        name='userlist'
        ),
    url(r'^(?P<pk>\d+)/$',
        apis.UserRetrieveUpdateDestroyView.as_view(),
        name='userinfo'
        ),
    url(r'signup/$',
        apis.UserSignupView.as_view(),
        name='signup'
        ),
    url(r'^login/$',
        apis.CustomAuthTokenView.as_view(),
        name='login'
        ),
    url(r'^logout/$',
        apis.UserLogoutView.as_view(),
        name='logout'
        ),
    url(r'^(?P<pk>\d+)/edit/$',
        apis.UserRetrieveUpdateDestroyView.as_view(),
        name='userinfo_update'
        ),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        apis.AccountActivationView.as_view(),
        name='activate'),
]
