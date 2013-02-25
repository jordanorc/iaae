from django.conf.urls import patterns, include, url
from iaae.views import IndexView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',   
    url(r'^$', IndexView.as_view(), name="index"), 
    (r'^mail/', include('mail.urls', namespace='mail')),   
    (r'^vle/', include('vle.urls', namespace='vle')),   
)