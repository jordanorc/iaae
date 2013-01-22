from django.conf.urls import patterns, include, url
from nlp.views import NlpView, IndexView, processing_view

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name="index_view"),
    url(r'^nlp/$', NlpView.as_view(), name="nlp_view"),
    url(r'^nlp/processing/$', processing_view, name="nlp_email_processing"),
    (r'^mail/', include('mail.urls', namespace='mail')),    
)