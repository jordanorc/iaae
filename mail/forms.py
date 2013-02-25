# -*- coding: utf-8 -*-
from django import forms
from mail.models import Email, EMAIL_TAGS
from django.utils.html import strip_tags

class SendMailForm(forms.ModelForm):
    
    class Meta:
        model = Email
        
class ReplyEmailForm(forms.Form):
    
    message = forms.CharField(widget=forms.Textarea)
    
class EmailMarkForm(forms.Form):

    tag = forms.ChoiceField(choices=EMAIL_TAGS, widget=forms.HiddenInput)

class EmailActionForm(forms.Form):
    
    emails = forms.ModelMultipleChoiceField(queryset=Email.objects.all(), widget=forms.CheckboxSelectMultiple)
    tag = forms.ChoiceField(choices=EMAIL_TAGS, widget=forms.HiddenInput)
    
    
'''
Processing forms
'''
class NlpForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

    def clean(self):
        if self.cleaned_data.get('text', None):
            self.cleaned_data['text'] = strip_tags(self.cleaned_data['text'])
        return super(NlpForm, self).clean()

class ProcessingStepOneForm(forms.Form):
    email = forms.ModelChoiceField(queryset=Email.emails.all())

class ProcessingStepTwoForm(forms.Form):
    next = forms.BooleanField(widget=forms.HiddenInput, initial=True)

class ProcessingStepThreeForm(forms.Form):
    next = forms.BooleanField(widget=forms.HiddenInput, initial=True)

class ProcessingStepFourForm(forms.Form):
    next = forms.BooleanField(widget=forms.HiddenInput, initial=True)