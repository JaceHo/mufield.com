from django.conf.urls import url, patterns
from rest_framework.urlpatterns import format_suffix_patterns

from apps.api.v1.relationship import views


'''
router = DefaultRouter()
router.register('', views.AuthenticatedUserFriendShipViewSet)
urlpatterns = router.urls
print(urlpatterns)
'''

urlpatterns = patterns(r'',
                       url(r'^user/contact/$',
                           views.UserContactList.as_view(),
                           name='user-contact-list'),
                       url(r'^user/contact/(?P<pk>[\w.+-]+)/$',
                           views.UserContactList.as_view(), name='user-contact-detail'),
                       # all groups
                       url(r'^groups/$',
                           views.GroupList.as_view(), name='group-list'),

                       url(r'^user/group/$',
                           views.UserGroupContactList.as_view(),
                           name='user-group-contact-list'),
                       url(r'^user/group/(?P<pk>[\w.+-]+)/$',
                           views.UserGroupContactList.as_view(), name='user-group-contact-detail'),

                       url(r'^user/groups/$',
                           views.UserGroupList.as_view(),
                           name='user-group-list'),
                       # group details
                       url(r'^groups/(?P<pk>[\w.+-]+)/$',
                           views.GroupDetail.as_view(), name='group-detail'),

                       # group membership management
                       url(r'^groups/(?P<pk>[\w.+-]+)/members/(?P<username>[\w.+-]+)/$',
                           views.GroupMemberDetail.as_view(),
                           name='group-member-detail'),

                       url(r'^user/friends/$',
                           views.UserFriendList.as_view(),
                           name='user-friend-list'),
                       url(r'^user/friend/$',
                           views.UserFriendContactList.as_view(),
                           name='user-friend-contact-list'),
                       url(r'^user/friend/(?P<pk>[\w.+-]+)/$',
                           views.UserFriendContactDetail.as_view(), name='user-friend-contact-detail'),

                       # all friendships
                       url(r'^friendships/$',
                           views.FriendshipList.as_view(), name='friendship-list'),
                       # friendship details
                       url(r'^friendships/(?P<pk>[\w.+-]+)/$',
                           views.FriendshipDetail.as_view(), name='friendship-detail'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
