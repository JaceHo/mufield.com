from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve as serve_static
from django.views.decorators.cache import never_cache
from django.contrib import admin
from compressor.conf import *

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^api/', include('apps.api.urls')),
                       url('', include('apps.home.urls')),
                       url('', include('apps.chat.urls')),
                       url('', include('apps.csp.urls')),
                       url('', include('apps.flatpages.urls')),
                       url('', include('apps.join.urls')),
                       url('', include('apps.sitemap.urls')),
                       url('', include('apps.online.urls')),
                       url(r'^friends/suggestions/', include('apps.friendship.contrib.suggestions.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # templiy for easy use

handler404 = 'apps.join.views.e404'
handler500 = 'apps.join.views.e500'

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
    )

    urlpatterns += patterns('django.views.static',
                            url(r'^static/(?P<path>.*)$', never_cache(serve_static)),
    )
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

