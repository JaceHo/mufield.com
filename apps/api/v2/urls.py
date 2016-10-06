from django.conf.urls import url, patterns

urlpatterns = patterns('',
                        url(r'^$', 'apps.api.v1.views.api_root', name='api_root'),
)

