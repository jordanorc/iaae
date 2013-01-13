# -*- coding: utf-8 -*-
from django import forms

class NlpForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

