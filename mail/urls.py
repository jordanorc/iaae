# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from mail.views import ComposeMailView, InboxView, MailView

urlpatterns = patterns('email',
    # urls para recursos
    url(r'^compose/$', ComposeMailView.as_view(), name='compose'),
    url(r'^reply/$', ComposeMailView.as_view(), name='reply'),
    url(r'^inbox/(?P<pk>\d+)/$', MailView.as_view(), name='mail'),
    url(r'^inbox/$', InboxView.as_view(), name='inbox'),
)
