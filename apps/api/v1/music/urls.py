from django.conf.urls import patterns, url
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from apps.api.v1.music import views


router = DefaultRouter()

router.register(r'artists', views.SingerViewSet)
router.register(r'musics', views.MusicViewSet)
urlpatterns = patterns('',
                       url(r'^fieldnames/$', views.FieldNameListView.as_view(),
                           name='fieldname-list'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += router.urls
