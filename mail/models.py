# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Email(models.Model):
    subject = models.CharField(_(u"Subject"), max_length=255)
    from_name = models.CharField(_(u"From Name"), max_length=50)
    from_email = models.EmailField(_(u"From Email"))
    message = models.TextField(_(u'Message'))
    parent = models.ForeignKey('Email', editable=False, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(editable=False, default=False)
    
    def title(self):
        print "%s - %s" % (self.subject, self.message)[:65]
        return "%s - %s" % (self.subject, self.message)[0:65]

    def __unicode__(self):
        return self.subject

    class Meta:
        ordering = ('-date',)