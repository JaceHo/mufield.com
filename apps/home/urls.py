from django.conf.urls import patterns, url


urlpatterns = patterns('',
                       url(r'^$', 'apps.home.views.index'),
)
