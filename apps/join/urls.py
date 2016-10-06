from django.conf.urls import patterns, url

from apps.join.views import HomeView, CreateView

urlpatterns = patterns('',
                       url(r'^join$', HomeView.as_view()),
                       url(r'^create-chat/$', CreateView.as_view()),
)
