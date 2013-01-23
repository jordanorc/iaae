# -*- coding: utf-8 -*-
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