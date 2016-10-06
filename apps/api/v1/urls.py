from django.conf.urls import url, include, patterns
from rest_framework.urlpatterns import format_suffix_patterns

from apps.api.v1 import views


urlpatterns = patterns('', url(r'^token/', views.TokenView.as_view(), name='token'), )
urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += patterns('',
                        url(r'^$', 'apps.api.v1.views.api_root', name='api_root'),
                        url(r'', include('apps.api.v1.account.urls')),
                        url(r'', include('apps.api.v1.relationship.urls')),
                        url(r'', include('apps.api.v1.conversation.urls')),
                        url(r'', include('apps.api.v1.music.urls')),
                        url(r'', include('apps.api.v1.feedback.urls')),
                        url(r'', include('apps.api.v1.explore.urls')),
                        url(r'', include('apps.api.v1.search.urls')),
)

