# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.urlresolvers import reverse
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView
from mail.models import Email
from nlp.forms import NlpForm, ProcessingStepOneForm, ProcessingStepTwoForm, \
    ProcessingStepThreeForm, ProcessingStepFourForm
from nlp.visl import Visl
from nltk.corpus import stopwords
import nltk

class IndexView(RedirectView):
    
    def get_redirect_url(self):
        return reverse("mail:inbox")

class NlpView(FormView):
    template_name = 'nlp.html'
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
        return reverse('nlp_view')


class ProcessingWizard(SessionWizardView):
    template_name = "processing.html"
    form_list = (ProcessingStepOneForm, ProcessingStepTwoForm)
    
    def get_context_data(self, form, **kwargs):
        context = super(ProcessingWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == 'step_one':
            context.update({'emails': Email.objects.all()})
        elif self.steps.current == 'step_two':
            cleaned_data = self.get_cleaned_data_for_step(self.steps.prev)
            email = cleaned_data['email']
            
            visl = Visl()
            context['email_tagged'] = visl.tag(email.raw_message)
            
            filtered_message = email.raw_message.split(" ") #make a copy of the word_list
            for key, word in enumerate(filtered_message): # iterate over word_list
                if word in stopwords.words('portuguese'): 
                    filtered_message[key] = "*"
                    
            context['filtered_message'] = " ".join(filtered_message)
            
            context.update({'email': cleaned_data['email']})
            
        return context
    
    def get_template_names(self):
        return ["steps/%s.html" % (self.steps.current,)]
    
processing_view = ProcessingWizard.as_view((
    ("step_one", ProcessingStepOneForm),
    ("step_two", ProcessingStepTwoForm),
    ("step_three", ProcessingStepThreeForm),
    ("step_four", ProcessingStepFourForm)
))
