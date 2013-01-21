# -*- coding: utf-8 -*-
from nlp.forms import NlpForm
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from nltk.tag import UnigramTagger
from nltk.corpus import mac_morpho
import nltk
from django.conf import settings
from BeautifulSoup import BeautifulSoup
import urllib
import urllib2

class Visl(object):

    url = "http://beta.visl.sdu.dk/visl/pt/parsing/automatic/parse.php"
    params = {'inputlang': 'pt', 'parser': 'morphdis', 'visual': 'niceline'}

    def tag(self, text):
        params = self.params.copy()
        params['text'] = text.encode('utf-8')
        params = urllib.urlencode(params)
        req = urllib2.Request(self.url, params)
        response = urllib2.urlopen(req).read()

        soup = BeautifulSoup(response, convertEntities=BeautifulSoup.HTML_ENTITIES)

        tagged_text = []
        for word in soup.find('dl').findAllNext('dt'):
            tags = []
            if word.find('font', attrs={'color': 'blue'}):
                tags.append(word.findAllNext('font')[0].text)
                tags.append(word.findAllNext('font')[2].findNext('b').extract().text)
                tags.append(word.findAllNext('font')[1].text)
                tags.append(word.findAllNext('font')[2].text)
            else:
                tags.append(word.findAllNext('font')[0].text)
                tags.append(word.findAllNext('font')[0].text)
                
            tagged_text.append(tags)

        return tagged_text


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

        #print etiquetador.evaluate(sentencas_treinadoras)

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
