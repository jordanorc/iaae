# -*- coding: utf-8 -*-
from core.aiml_util import check_answer
from core.forms import NlpForm, ProcessingStepOneForm, ProcessingStepTwoForm, \
    ProcessingStepThreeForm, ProcessingStepFourForm
from core.visl import Visl
from django.conf import settings
from django.contrib import messages
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import FormView
from mail.models import Email, EMAIL_TAGS
from nltk.corpus import stopwords
import copy
import nltk

class NlpView(FormView):
    template_name = 'core/nlp.html'
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
        return reverse('nlp:nlp')


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
        return redirect(reverse('nlp:processing'))
            
    
    def get_template_names(self):
        return ["core/processing/steps/%s.html" % (self.steps.current,)]
    
processing_view = ProcessingWizard.as_view((
    ("step_one", ProcessingStepOneForm),
    ("step_two", ProcessingStepTwoForm),
    ("step_three", ProcessingStepThreeForm),
    ("step_four", ProcessingStepFourForm)
))
