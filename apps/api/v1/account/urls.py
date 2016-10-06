from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from apps.api.v1.account import views



# URL structure inspired by github API: https://developer.github.com/v3/users/

urlpatterns = patterns('',
                       # user list, for public data representation
                       url(r'^users/$',
                           views.UserList.as_view(),
                           name='user-list'),

                       # user details and list of a single user
                       url(r'^users/(?P<username>[\w.+-]+)/$',
                           views.UserDetail.as_view(),
                           name='user-detail'),

                       # user sms verification
                       url(r'^sms/$',
                           views.VerifiedActionView.as_view(),
                           name='users-sms'),

                       # authenticated user's details and associated lists
                       url(r'^user/$',
                           views.AuthenticatedUserDetail.as_view(),
                           name='user-auth-detail'),
                       url(r'^user/geo/$',
                           views.UserNearbyList.as_view(),
                           name='user-nearby-list'),
                       url(r'^user/similar/$',
                           views.UserSimilarList.as_view(),
                           name='user-similar-list'),
                       url(r'^user/posts/$',
                           views.UserPostList.as_view(),
                           name='user-post-list'),
                       url(r'^user/fields/$',
                           views.UserFieldList.as_view(),
                           name='user-field-list'),
                       url(r'^user/fields/(?P<pk>[\w.+-]+)$',
                           views.UserFieldDetail.as_view(),
                           name='user-field-detail'),
                       url(r'^user/topics/$',
                           views.UserTopicList.as_view(),
                           name='user-music-list'),
                       url(r'^user/musics/$',
                           views.UserMusicList.as_view(),
                           name='user-music-list'),
                       url(r'^user/musics/(?P<pk>[\w.+-]+)$',
                           views.UserMusicDetail.as_view(),
                           name='user-music-detail'),

                       url(r'^user/fields/(?P<pk>[\w.+-]+)/torrents$',
                           views.UserFieldTorrentList.as_view(),
                           name='user-field-torrent-list'),
                       )

urlpatterns = format_suffix_patterns(urlpatterns)

