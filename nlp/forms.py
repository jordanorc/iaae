# -*- coding: utf-8 -*-
from django import forms
from django.contrib.formtools.wizard.views import SessionWizardView
from django.shortcuts import render_to_response
from mail.models import Email

class NlpForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)


class ProcessingStepOneForm(forms.Form):
    email = forms.ModelChoiceField(queryset=Email.objects.all())

class ProcessingStepTwoForm(forms.Form):
    next = forms.BooleanField(widget=forms.HiddenInput, initial=True)

class ProcessingStepThreeForm(forms.Form):
    next = forms.BooleanField(widget=forms.HiddenInput, initial=True)

class ProcessingStepFourForm(forms.Form):
    next = forms.BooleanField(widget=forms.HiddenInput, initial=True)

class ProcessingWizard(SessionWizardView):
    template_name="processing.html"
    form_list = (ProcessingStepOneForm, ProcessingStepTwoForm)
    
    def get_context_data(self, form, **kwargs):
        context = super(ProcessingWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == 'step_one':
            context.update({'emails': Email.objects.all()})
        return context
    
processing_view = ProcessingWizard.as_view((
    ("step_one", ProcessingStepOneForm), 
    ("step_two", ProcessingStepTwoForm), 
    ("step_three", ProcessingStepThreeForm), 
    ("step_four", ProcessingStepFourForm)
))
