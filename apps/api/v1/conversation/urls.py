from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from apps.api.v1.conversation import views


urlpatterns = patterns('',

                       url(r'^user/requests/$',
                           views.UserRequestList.as_view(),
                           name='user-request-list'),

                       # authenticated user request's details and associated lists
                       url(r'^user/requests/(?P<pk>[\w.+-]+)/$',
                           views.RequestDetailViewPart.as_view(),
                           name='user-request-detail'),

                       url(r'^user/chats/$',
                           views.UserChatList.as_view(),
                           name='user-chat-list'),

                       # post details
                       url(r'^posts/(?P<pk>[\w.+-]+)/$',
                           views.PostDetail.as_view(),
                           name='post-detail'),

                       # chat details
                       url(r'^chats/(?P<pk>[\w.+-]+)/$',
                           views.ChatDetail.as_view(),
                           name='chat-detail'),

                       # chat messages
                       url(r'^chats/(?P<pk>[\w.+-]+)/messages/$',
                           views.ChatMessageList.as_view(),
                           name='chat-message-list'),
)
urlpatterns = format_suffix_patterns(urlpatterns)
