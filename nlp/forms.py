# -*- coding: utf-8 -*-
from django import forms
from django.utils.html import strip_tags
from mail.models import Email

class NlpForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

    def clean(self):
        if self.cleaned_data.get('text', None):
            self.cleaned_data['text'] = strip_tags(self.cleaned_data['text'])
        return super(NlpForm, self).clean()

class ProcessingStepOneForm(forms.Form):
    email = forms.ModelChoiceField(queryset=Email.objects.all())

class ProcessingStepTwoForm(forms.Form):
    next = forms.BooleanField(widget=forms.HiddenInput, initial=True)

class ProcessingStepThreeForm(forms.Form):
    next = forms.BooleanField(widget=forms.HiddenInput, initial=True)

class ProcessingStepFourForm(forms.Form):
    next = forms.BooleanField(widget=forms.HiddenInput, initial=True)