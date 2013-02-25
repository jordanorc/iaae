# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import modelformset_factory
from vle.models import Thesis, Student, Discussion

class DiscussionForm(forms.ModelForm):
    
    automatically_generate = forms.BooleanField(label="Automatically generate", required=False)
    
    formset_class = None
    formset = None
    
    def __init__(self, *args, **kwargs):
        super(DiscussionForm, self).__init__(*args, **kwargs)
        self.formset_class = modelformset_factory(Thesis, max_num=100, extra=1)
        queryset = Thesis.objects.none()
        instance = kwargs.get("instance", None)
        if instance:
            queryset = Thesis.objects.filter(discussion=instance)
            del self.fields["automatically_generate"]
        self.formset = self.formset_class(queryset=queryset)
        
    def clean(self):
        cleaned_data = self.cleaned_data
        automatically_generate = cleaned_data.get("automatically_generate")
        self.cleaned_data["theses"] = None

        # get theses
        if self.data:
            self.formset = self.formset_class(self.data, self.files, queryset=Thesis.objects.none())
            if self.formset.is_valid() and self.is_valid():                
                self.cleaned_data["theses"] = self.formset.cleaned_data
                if not automatically_generate and len(filter(None, self.cleaned_data["theses"])) < self.cleaned_data["number_theses"]:
                    raise forms.ValidationError("You have to write %s theses." % self.cleaned_data["number_theses"])
            
        return cleaned_data          

    class Meta:
        model = Discussion
        
class DiscussionThesisForm(forms.Form):
    data = forms.CharField()