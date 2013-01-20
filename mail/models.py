# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

class EmailManager(models.Manager):
    
    def get_query_set(self):
        queryset = super(EmailManager, self).get_query_set()
        queryset = queryset.filter(parent__isnull=True)
        return queryset
    

class Email(models.Model):
    subject = models.CharField(_(u"Subject"), max_length=255)
    from_name = models.CharField(_(u"From Name"), max_length=50)
    from_email = models.EmailField(_(u"From Email"))
    message = models.TextField(_(u'Message'))
    parent = models.ForeignKey('Email', editable=False, null=True, blank=True, related_name="threads")
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(editable=False, default=False)
    important = models.BooleanField(editable=False, default=False)
    spam = models.BooleanField(editable=False, default=False)
    trash = models.BooleanField(editable=False, default=False)
    
    objects = models.Manager()
    emails = EmailManager()
    
    def title(self):
        return "%s - %s" % (self.subject, self.message)[0:65]

    @property
    def respondido(self):
        print self.threads.count()
        return self.threads.count() > 0
        
    def __unicode__(self):
        return self.subject

    class Meta:
        ordering = ('-date',)