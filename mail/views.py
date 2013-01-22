# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from mail.forms import SendMailForm, ReplyEmailForm, EmailActionForm, \
    EmailMarkForm
from mail.models import Email, EMAIL_TAGS
from util.forms.multi import MultiFormView, FormProvider

class ComposeMailView(CreateView):
    form_class = SendMailForm
    template_name = 'mail/compose.html'
    
    def form_valid(self, form):
        messages.success(self.request, _(u'Your message has been sent'))
        return super(ComposeMailView, self).form_valid(form)
    
    def get_success_url(self):
        return reverse('mail:inbox')
    
def ReplyEmailView(FormView):
    form = ReplyEmailForm

class InboxView(ListView, FormView):
    model = Email
    template_name = 'mail/inbox.html'
    queryset = Email.emails.all()
    form_class = EmailActionForm
    
    def get_context_data(self, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        data = ListView.get_context_data(self, object_list=self.object_list)
        data['form'] = form
        data['EMAIL_TAGS'] = EMAIL_TAGS
        return data 
    
    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        
        emails = cleaned_data['emails']
        tag = int(cleaned_data['tag'])
        
        for email in emails:
            email.mark(tag)
        
        if tag == EMAIL_TAGS.TRASH:
            messages.success(self.request, _(u'The message has been moved to the Trash.'))

        elif tag == EMAIL_TAGS.SPAM:
            messages.success(self.request, _(u'The message has been marked as spam.'))
            
        elif tag == EMAIL_TAGS.READ:
            messages.success(self.request, _(u'The message has been marked as read.'))
            
        elif tag == EMAIL_TAGS.IMPORTANT:
            messages.success(self.request, _(u'The message has been marked as important.'))
        
        return FormView.form_valid(self, form)
    
    def get_success_url(self):
        return reverse('mail:inbox')
    
    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            raise Http404(_(u"Empty list and '%(class_name)s.allow_empty' is False.")
                          % {'class_name': self.__class__.__name__})
        return FormView.post(self, request, *args, **kwargs)
    
class MailView(DetailView, MultiFormView):
    model = Email
    template_name = 'mail/mail.html' 
    forms = {
         'reply': FormProvider(ReplyEmailForm, 'form'),
         'action': FormProvider(EmailMarkForm, 'form'),
     }
    groups = {'reply': ('reply',), 'action': ('action', )}
    
    def valid_reply(self, forms):
        import copy
        cleaned_data = forms['reply'].cleaned_data
        
        resposta = copy.deepcopy(self.object)
        resposta.id = None
        resposta.message = cleaned_data['message']
        resposta.parent = self.object
        resposta.full_clean()
        resposta.save()
        
    def valid_action(self, forms):
        cleaned_data = forms['action'].cleaned_data
        
        tag = int(cleaned_data["tag"])
        
        if tag == EMAIL_TAGS.TRASH:
            messages.success(self.request, _(u'The message has been moved to the Trash.'))

        elif tag == EMAIL_TAGS.SPAM:
            messages.success(self.request, _(u'The message has been marked as spam.'))
            
        elif tag == EMAIL_TAGS.READ:
            messages.success(self.request, _(u'The message has been marked as read.'))
            
        elif tag == EMAIL_TAGS.IMPORTANT:
            messages.success(self.request, _(u'The message has been marked as important.'))
        
    def get_success_url(self):
        return reverse('mail:mail', args=(self.object.pk,))
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return MultiFormView.post(self, request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        forms = MultiFormView.construct_forms(self)
        data = DetailView.get_context_data(self, object=self.object)
        data.update(forms)
        data['EMAIL_TAGS'] = EMAIL_TAGS
        return data
    