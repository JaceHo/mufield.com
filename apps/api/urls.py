from django.conf.urls import *

urlpatterns = patterns('',
                       # login and logout views for the browseable API
                       url(r'', include('rest_framework.urls',
                                        namespace='rest_framework')),
                       url(r'^v1/', include('apps.api.v1.urls', namespace='v1')),
                       url(r'^v2/', include('apps.api.v2.urls', namespace='v2')),
                       url(r'^docs/', include('rest_framework_swagger.urls')),
                       )
