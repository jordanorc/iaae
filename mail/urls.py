# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from mail.views import ComposeMailView, InboxView, MailView, NlpView, processing_view,\
    AboutView

urlpatterns = patterns('email',
    # urls para recursos
    url(r'^about/$', AboutView.as_view(), name='about'),
    url(r'^compose/$', ComposeMailView.as_view(), name='compose'),
    url(r'^reply/$', ComposeMailView.as_view(), name='reply'),
    url(r'^inbox/(?P<pk>\d+)/$', MailView.as_view(), name='mail'),
    url(r'^inbox/$', InboxView.as_view(), name='inbox'),
    
    url(r'^nlp/$', NlpView.as_view(), name="nlp"),
    url(r'^processing/$', processing_view, name="processing"),
)