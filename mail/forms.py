# -*- coding: utf-8 -*-
from django import forms
from mail.models import Email

class SendMailForm(forms.ModelForm):
    
    class Meta:
        model = Email
        
class ReplyEmailForm(forms.Form):
    
    message = forms.CharField(widget=forms.Textarea)

ACTION_TRASH = 1
ACTION_MARK_AS_SPAM = 2
ACTION_MARK_AS_READ = 3
ACTION_MARK_AS_IMPORTANT = 4

ACTION_CHOICES = (
     (ACTION_TRASH, "Send to trash"),
     (ACTION_MARK_AS_SPAM, "Mark as spam"),
     (ACTION_MARK_AS_READ, "Mark as read"),
     (ACTION_MARK_AS_IMPORTANT, "Mark as important"),
)
    
class EmailActionForm(forms.Form):
    
    emails = forms.ModelMultipleChoiceField(queryset=Email.objects.all(), widget=forms.CheckboxSelectMultiple)
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.HiddenInput)