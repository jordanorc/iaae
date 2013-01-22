# -*- coding: utf-8 -*-
from django import forms
from mail.models import Email, EMAIL_TAGS

class SendMailForm(forms.ModelForm):
    
    class Meta:
        model = Email
        
class ReplyEmailForm(forms.Form):
    
    message = forms.CharField(widget=forms.Textarea)

class EmailActionForm(forms.Form):
    
    emails = forms.ModelMultipleChoiceField(queryset=Email.objects.all(), widget=forms.CheckboxSelectMultiple)
    tag = forms.ChoiceField(choices=EMAIL_TAGS, widget=forms.HiddenInput)