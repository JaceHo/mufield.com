from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^online/$', 'apps.online.views.index'),
                       url(r'^online/order$', 'apps.online.views.order'),
)

