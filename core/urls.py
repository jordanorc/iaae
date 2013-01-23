from django.conf.urls import patterns, include, url
from core.views import NlpView, processing_view

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', NlpView.as_view(), name="nlp"),
    url(r'^processing/$', processing_view, name="processing"),
)