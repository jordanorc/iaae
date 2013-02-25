# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from mail.aiml_util import check_answer
from mail.forms import NlpForm, ProcessingStepOneForm, ProcessingStepTwoForm, \
    ProcessingStepThreeForm, ProcessingStepFourForm, SendMailForm, ReplyEmailForm, \
    EmailActionForm, EmailMarkForm
from mail.models import Email, EMAIL_TAGS
from util.forms.multi import MultiFormView, FormProvider
from util.visl import Visl
import copy
import nltk
from django.conf import settings

class AboutView(TemplateView):
    
    template_name = "mail/about.html"
    
    def get_context_data(self, **kwargs):
        data = super(AboutView, self).get_context_data(**kwargs)
        data["text"] = open(settings.PROJECT_DIR + '/../docs/about.txt', 'r').read()
        return data

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
    
'''
E-mail processing views
'''
class NlpView(FormView):
    template_name = 'mail/nlp.html'
    form_class = NlpForm

    def form_valid(self, form, **kwargs):
        context = {}

        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        etiquetador = settings.ETIQUETADOR
        frases = form.cleaned_data['text']

        # segmenta texto em sentenças
        sentences_tokenizer = nltk.data.load('tokenizers/punkt/portuguese.pickle')
        sentences = sentences_tokenizer.tokenize(frases)

        # armazena sentenças taggeadas
        context['text'] = frases
        context['sentences'] = sentences
        context['tagged_sentences'] = []
        context['tagged_sentences_visl'] = []

        for sentence in sentences:
            context['tagged_sentences'].append(etiquetador.tag(nltk.word_tokenize(sentence)))
            visl = Visl()
            context['tagged_sentences_visl'].append(visl.tag(sentence))

        context['show_sentences'] = True

        self.request.session['context'] = context
        
        return super(NlpView, self).form_valid(form)
    
    def get_initial(self):
        if self.request.session.get('context', None):
            return {'text': self.request.session['context']['text']}
        else:
            return {}

    def get_context_data(self, **kwargs):
        if self.request.session.get('context', None):
            kwargs.update(self.request.session.get('context').copy())
            del self.request.session['context']
        return super(NlpView, self).get_context_data(**kwargs)

    def get_success_url(self):
        return reverse('mail:nlp')


class ProcessingWizard(SessionWizardView):
    form_list = (ProcessingStepOneForm, ProcessingStepTwoForm)
    
    def get_context_data(self, form, **kwargs):
        context = super(ProcessingWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == 'step_one':            
            emails = Email.emails.unreplied().filter(tags__tag=EMAIL_TAGS.QUESTION)
            context.update({'emails': emails})
        elif self.steps.current == 'step_two':
            cleaned_data = self.get_cleaned_data_for_step(self.steps.first)
            email = cleaned_data['email']            
            context.update({'email': email})
            
        elif self.steps.current == 'step_four':
            cleaned_data = self.get_cleaned_data_for_step(self.steps.first)
            email = cleaned_data['email']      
            answer = check_answer(email.raw_message)      
            context.update({'email': email.raw_message, 'answer': answer})
            
        return context
    
    def done(self, form_list, **kwargs):
        cleaned_data = self.get_cleaned_data_for_step(self.steps.first)
        email = cleaned_data['email']   
        answer = check_answer(email.raw_message)      
        if answer:
            resposta = copy.deepcopy(email)
            resposta.id = None
            resposta.message = answer
            resposta.parent = email
            resposta.full_clean()
            resposta.save()
            messages.success(self.request, _(u'Your reply was automatically sent.'))
        else:
            messages.warning(self.request, _(u'The answer to your question was not found.'))
        return redirect(reverse('mail:processing'))
            
    
    def get_template_names(self):
        return ["mail/processing/steps/%s.html" % (self.steps.current,)]
    
processing_view = ProcessingWizard.as_view((
    ("step_one", ProcessingStepOneForm),
    ("step_two", ProcessingStepTwoForm),
    ("step_three", ProcessingStepThreeForm),
    ("step_four", ProcessingStepFourForm)
))
