# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, ListView
from django.views.generic.detail import DetailView
from mail.forms import SendMailForm
from mail.models import Email

class SendMailView(CreateView):
    form_class = SendMailForm
    template_name = 'mail/send.html'
    
    def form_valid(self, form):
        messages.success(self.request, _(u'Your message has been sent'))
        return super(SendMailView, self).form_valid(form)
    
    def get_success_url(self):
        return reverse('mail:send_mail')

class InboxView(ListView):
    model = Email
    template_name = 'mail/inbox.html'
    
class MailView(DetailView):
    model = Email
    template_name = 'mail/mail.html' 