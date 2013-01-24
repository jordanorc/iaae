# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.views.generic.base import RedirectView, TemplateView
from settings import PROJECT_DIR


class IndexView(RedirectView):
    
    def get_redirect_url(self):
        return reverse("about")
    
class AboutView(TemplateView):
    
    template_name = "about.html"
    
    def get_context_data(self, **kwargs):
        data = super(AboutView, self).get_context_data(**kwargs)
        data["text"] = open(PROJECT_DIR + '/../docs/about.txt', 'r').read()
        return data