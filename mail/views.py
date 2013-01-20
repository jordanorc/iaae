# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from mail.forms import SendMailForm, ReplyEmailForm, EmailActionForm, \
    ACTION_TRASH, ACTION_MARK_AS_SPAM, ACTION_MARK_AS_READ, ACTION_MARK_AS_IMPORTANT
from mail.models import Email

class SendMailView(CreateView):
    form_class = SendMailForm
    template_name = 'mail/send.html'
    
    def form_valid(self, form):
        messages.success(self.request, _(u'Your message has been sent'))
        return super(SendMailView, self).form_valid(form)
    
    def get_success_url(self):
        return reverse('mail:send_mail')
    
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
        return data 
    
    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        
        emails = cleaned_data['emails']
        if int(cleaned_data['action']) == ACTION_TRASH:
            emails.update(trash=True)
            messages.success(self.request, _(u'The message has been moved to the Trash.'))
            
        elif int(cleaned_data['action']) == ACTION_MARK_AS_SPAM:
            emails.update(spam=True)
            messages.success(self.request, _(u'The message has been marked as spam.'))
            
        elif int(cleaned_data['action']) == ACTION_MARK_AS_READ:
            emails.update(read=True)
            messages.success(self.request, _(u'The message has been marked as read.'))
            
        elif int(cleaned_data['action']) == ACTION_MARK_AS_IMPORTANT:
            messages.success(self.request, _(u'The message has been marked as important.'))
            emails.update(important=True)
        
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
    
class MailView(DetailView, FormView):
    model = Email
    template_name = 'mail/mail.html' 
    form_class = ReplyEmailForm
    
    def form_valid(self, form):
        import copy
        cleaned_data = form.cleaned_data
        
        resposta = copy.deepcopy(self.object)
        resposta.id = None
        resposta.message = cleaned_data['message']
        resposta.parent = self.object
        resposta.full_clean()
        resposta.save()
        
        print resposta
        
        return FormView.form_valid(self, form)
    
    def get_success_url(self):
        return reverse('mail:mail', args=(self.object.pk,))
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return FormView.post(self, request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        data = DetailView.get_context_data(self, object=self.object)
        print data
        data['form'] = form
        return data
    