from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from apps.api.v1.feedback import views


urlpatterns = patterns('',
                       # submit feedback
                       url(r'^feedbacks/$', views.FeedbackSubmit.as_view(),
                           name='feedback-submit'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
