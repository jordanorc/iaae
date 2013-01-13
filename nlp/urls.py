from django.conf.urls import patterns, include, url
from nlp.views import NlpView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', NlpView.as_view(), name="nlp_view"),
    (r'^mail/', include('mail.urls', namespace='mail')),
)
