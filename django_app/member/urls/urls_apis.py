from django.conf.urls import url
from member import views, apis

urlpatterns = [
    url(r'^$', apis.UserListView.as_view(),
        name='userlist'),
    url(r'signup/$',
        apis.UserListView.as_view(),
        name='signup'),
    url(r'^login/$',
        apis.CustomAuthTokenView.as_view(),
        name='login'
        ),
    url(r'^logout/$',
        apis.UserLogoutView.as_view(),
        name='logout'
        ),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        apis.AccountActivationView.as_view(),
        name='activate'),

    # url(r'^signup/$', views.signup, name='signup'),
    # url(r'^login/$', views.login, name='login'),
    # url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #   views.activate, name='activate')
]
