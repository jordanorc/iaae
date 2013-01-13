# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from mail.views import SendMailView, InboxView, MailView

urlpatterns = patterns('inscricao.views',
    # urls para recursos
    url(r'^send/$', SendMailView.as_view(), name='send_mail'),
    url(r'^inbox/(?P<pk>\d+)/$', MailView.as_view(), name='mail'),
    url(r'^inbox/$', InboxView.as_view(), name='inbox'),
)