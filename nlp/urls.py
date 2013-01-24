from django.conf.urls import patterns, include, url
from nlp.views import IndexView, AboutView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',   
    url(r'^$', IndexView.as_view(), name="index"), 
    url(r'^about/$', AboutView.as_view(), name="about"), 
    (r'^nlp/', include('core.urls', namespace='nlp')),    
    (r'^mail/', include('mail.urls', namespace='mail')),   
)