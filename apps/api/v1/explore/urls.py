from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from apps.api.v1.explore import views


urlpatterns = patterns('',

                       url(r'^explore/$', views.explore_root,
                           name='explore_root'),

                       url(r'^explore/popular/$',
                           views.PopularGroupsList.as_view(),
                           name='explore-popular-list'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
