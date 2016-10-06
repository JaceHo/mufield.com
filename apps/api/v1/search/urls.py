from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from apps.api.v1.search import views


urlpatterns = patterns('',

                       url(r'^search/$', views.search_root, name='search_root'),

                       url(r'^search/users/$',
                           views.UserSearchResultList.as_view(),
                           name='user-search-list'),

                       url(r'^search/groups/$',
                           views.GroupSearchResultList.as_view(),
                           name='group-search-list'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
