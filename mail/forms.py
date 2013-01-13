# -*- coding: utf-8 -*-
from django import forms
from mail.models import Email

class SendMailForm(forms.ModelForm):
    
    class Meta:
        model = Email