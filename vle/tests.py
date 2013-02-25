"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson

class PollsViewsTestCase(TestCase):
    fixtures = [
        'test_data.json',
        ]
    
    def test_index(self):
        url = reverse('vle:discussion_to_generate')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('discussions' in resp.content)
        
    def test_log(self):
        slug = 1
        url = reverse('vle:ws_log', args=("agent-creator",))
        message = {'message': "test"}
        resp = self.client.post(url, {'data': simplejson.dumps(message)})
        print resp.content
        self.assertEqual(resp.status_code, 302)
        
    def test_discussion_generate(self):
        discussion_id = 1
        url = reverse('vle:discussion_generate', args=(discussion_id,))
        theses = [{'description': 'Tom is a cat', 'valid': True}]
        theses.append({'description': 'Jerry is a mouse', 'valid': True})
        theses.append({'description': 'Bugs Bunny is a rabbit', 'valid': True})
        resp = self.client.post(url, {'data': simplejson.dumps(theses)})
        print resp.content
        #self.assertEqual(resp.status_code, 302)