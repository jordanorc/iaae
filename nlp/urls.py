from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from nlp.forms import processing_view
from nlp.views import NlpView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', NlpView.as_view(), name="nlp_view"),
    url(r'^processing/$', processing_view, name="nlp_email_processing"),
    (r'^mail/', include('mail.urls', namespace='mail')),    
)
