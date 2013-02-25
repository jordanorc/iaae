# -*- coding: utf-8 -*-
from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView
from vle.forms import DiscussionForm, DiscussionThesisForm
from vle.models import Discussion, Thesis, Ontology, Log, Agent
import datetime
import json

class VleIndexView(TemplateView):
    template_name = "vle/index.html"

class ObjectDetailView(DetailView):
    pass
    
class ObjectCreateView(CreateView):
 
    def get_template_names(self):
        info = self.model._meta.app_label, self.model._meta.module_name
        templates = ['%s/%s/change.html' % info, '%s/change.html' % info[0], ]
        return templates

    def get_success_url(self):
        info = self.model._meta.app_label, self.model._meta.module_name
        return reverse("%s:%s_list" % info)
    
    def get_context_data(self, **kwargs):
        info = self.model._meta.app_label, self.model._meta.module_name
        context_data = super(ObjectCreateView, self).get_context_data(**kwargs)
        context_data['form_css_class'] = "%s-%s" % info
        return context_data
    
class ObjectUpdateView(UpdateView):

    def get_template_names(self):
        info = self.model._meta.app_label, self.model._meta.module_name
        templates = ['%s/%s/change.html' % info, '%s/change.html' % info[0], ]
        return templates
    
    def get_success_url(self):
        info = self.model._meta.app_label, self.model._meta.module_name
        return reverse("%s:%s_list" % info)
    
    def get_context_data(self, **kwargs):
        info = self.model._meta.app_label, self.model._meta.module_name
        context_data = super(ObjectUpdateView, self).get_context_data(**kwargs)
        context_data['form_css_class'] = "%s-%s" % info
        return context_data

def get_model_form(model_class, queryset=None):
    if not queryset:
        queryset = model_class.objects.all()
    class _ActionForm(forms.Form):
        objects = forms.ModelMultipleChoiceField(queryset=queryset, widget=forms.CheckboxSelectMultiple)
    return _ActionForm

class ObjectDeleteView(FormView):

    def get_form(self, form_class):
        return get_model_form(self.model)(**self.get_form_kwargs())
    
    def form_invalid(self, form):
        messages.warning(self.request, _(u'No objects selected.'))
        return super(ObjectDeleteView, self).form_invalid(form)
    
    def form_valid(self, form):
        info = self.model._meta.app_label, self.model._meta.module_name
        objects = form.cleaned_data['objects']
        objects.delete()
        messages.success(self.request, _(u'Objects removed.'))
        return redirect(reverse("%s:%s_list" % info))
        
class ObjectListView(ListView, ObjectDeleteView):
    paginate_by = 15
    list_display = ()
    
    def get_template_names(self):
        info = self.model._meta.app_label, self.model._meta.module_name
        templates = ['%s/%s/list.html' % info, '%s/list.html' % info[0], ]
        return templates
    
    def get_header(self):
        labels = self.get_labels_for(self.model())
        header = []
        for i, field_name in enumerate(self.list_display):
            h = {}
            if getattr(self, field_name, None):
                h['title'] = getattr(self, field_name).short_description
            else:
                h['title'] = labels[field_name]

            header.append(h)
        return header
    
    def get_labels_for(self, model, cap=True, esc=True):
        from django.template.defaultfilters import capfirst
        from django.utils.html import escape
        labels = {}
        for field in model._meta.fields:
            label = field.verbose_name
            if cap:
                label = capfirst(label)
            if esc:
                label = escape(label)
            labels[field.name] = label
        return labels

    def get_context_data(self, **kwargs):
        context_data = super(ObjectListView, self).get_context_data(object_list=self.object_list)
        form = ObjectDeleteView.get_form(self, None)
        context_data.update(ObjectDeleteView.get_context_data(self, form=form, view=self, header=self.get_header()))
        return context_data 

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            raise Http404(_(u"Empty list and '%(class_name)s.allow_empty' is False.")
                          % {'class_name': self.__class__.__name__})
        return ObjectDeleteView.post(self, request, *args, **kwargs)
    
class StudentListView(ObjectListView):
    list_display = ('first_name', 'date_birth', 'gender')
    
class TutorListView(ObjectListView):
    list_display = ('first_name', 'date_birth', 'gender')
    
class SubjectListView(ObjectListView):
    list_display = ('name',)
    
class CourseListView(ObjectListView):
    list_display = ('name',)
    
class SessionListView(ObjectListView):
    list_display = ('course', 'slug', 'year', 'semester')
    
class OntologyListView(ObjectListView):
    model = Ontology
    list_display = ('name', 'description')
    
class DiscussionListView(ObjectListView):
    model = Discussion
    list_display = ('id', 'title', 'session', 'number_theses')
    
class DiscussionCreateView(ObjectCreateView):
    form_class = DiscussionForm
    model = Discussion
    
    def form_valid(self, form):
        retorno = super(DiscussionCreateView, self).form_valid(form)        
        cleaned_data = form.cleaned_data

        if not cleaned_data.get("automatically_generate", False) and cleaned_data["theses"]:
            for t in cleaned_data["theses"]:
                thesis = Thesis(description=t["description"], discussion=self.object)
                thesis.full_clean()
                thesis.save()
                    
        return retorno
    
    def get_template_names(self):
        info = self.model._meta.app_label, self.model._meta.module_name
        templates = ['%s/%s/change.html' % info, '%s/change.html' % info[0], ]
        return templates
    
    def get_success_url(self):
        info = self.model._meta.app_label, self.model._meta.module_name
        return reverse("%s:%s_list" % info)
    
class AgentListView(ObjectListView):
    model = Agent
    list_display = ('slug', 'key')
    
class LogListView(ObjectListView):
    model = Log
    list_display = ('id', 'date', 'message')

class WSLogList(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        from django.template.defaultfilters import date as _date
        from django.conf import settings
        slug = kwargs.get("slug", None)
        agent = Agent.objects.get(slug=slug)
        pk = int(kwargs.get("pk")) if kwargs.get("pk", None) else None
        from django.core.serializers.json import DjangoJSONEncoder
        
        if pk:
            logs = agent.logs.filter(pk__gt = pk)
        else:
            logs = agent.logs.all()
        
        data = {"logs": [], 'pk': None}
        total = logs.count()

        if total:
            if not pk:
                logs = logs[total-11:]
            else:
                logs = logs[:10]
            total = logs.count()
            data["pk"] = logs[total-1].pk
            for log in logs:
                data["logs"].append({'pk': log.pk, 'date': _date(log.date, settings.SHORT_DATETIME_FORMAT), 'message': log.message})
        data = simplejson.dumps(data, cls=DjangoJSONEncoder)
            
        return HttpResponse(data, content_type='application/json')
    
class DiscussionUpdateView(ObjectUpdateView):

    form_class = DiscussionForm
    
class DiscussionThesesToGenerate(View):
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options', 'trace']

    def get(self, request, *args, **kwargs):
        discussions = Discussion.objects.filter(theses__isnull=True)
        data = {"discussions": []}
        for discussion in discussions:
            data["discussions"].append({'pk': discussion.pk, 'category': "Category", 'number_theses': discussion.number_theses})
        data = simplejson.dumps(data)
        
        return HttpResponse(data, content_type='application/json')

class OntologyView(View):
    http_method_names = ['get']

    def get(self, request, slug, *args, **kwargs):
        from django.core.servers.basehttp import FileWrapper
        ontology = Ontology.objects.get(slug=slug)
        wrapper = FileWrapper(ontology.file.file)
        
        return HttpResponse(wrapper, content_type='application/xhtml+xml')

class AgentMonitor(TemplateView):
    template_name = "vle/agents.html"

class DiscussionThesisGenerate(View):
    form_class = DiscussionThesisForm
    http_method_names = ['post']
    
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(DiscussionThesisGenerate, self).dispatch(request, *args, **kwargs)
    
    def process(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        # get discussion
        try:
            discussion = Discussion.objects.get(pk=pk)
        except Discussion.DoesNotExist:
            raise ValidationError('Discussion not found')
        
        data = request.POST.get('data', None)
        if not data:
            raise ValidationError('Invalid POST request')
        
        data = json.loads(data)
        for t in data:
            thesis = Thesis(description=t["description"], valid=t["valid"], discussion=discussion)
            thesis.full_clean()
            thesis.save()
            print t["valid"]
            print t["description"]
    
    def post(self, request, *args, **kwargs):
        print "aqui post foi"
        print request.POST
        response = {}
        try:
            self.process(request, *args, **kwargs)
            response['status'] = 'ok'
        except ValidationError as e:
            response['status'] = 'error'
            response['error'] = " ".join(e.messages)
            
        return HttpResponse(response, content_type='application/json')
    
    
class LogRegistry(View):
    http_method_names = ['post']
    
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(LogRegistry, self).dispatch(request, *args, **kwargs)
    
    def log(self, request):
        # get discussion
        data = request.POST.get('data', None)
        if not data:
            raise ValidationError('Invalid POST request')
        
        data = json.loads(data)
        log = Log(message=data["message"])
        log.save()
        self.agent.logs.add(log)
    
    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug', None)
        print slug
        try:
            self.agent = Agent.objects.get(slug=slug)
        except Discussion.DoesNotExist:
            raise ValidationError('Agent not found')
        
        response = {}
        try:
            self.log(request)
            response['status'] = 'ok'
        except ValidationError as e:
            response['status'] = 'error'
            response['error'] = " ".join(e.messages)
            
        return HttpResponse(response, content_type='application/json')
