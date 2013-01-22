# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags

class EmailManager(models.Manager):
    
    def get_query_set(self):
        queryset = super(EmailManager, self).get_query_set()
        queryset = queryset.filter(parent__isnull=True)
        return queryset
    

class Enumeration(object):
    """
    A small helper class for more readable enumerations,
    and compatible with Django's choice convention.
    You may just pass the instance of this class as the choices
    argument of model/form fields.

    Example:
        MY_ENUM = Enumeration([
            (100, 'MY_NAME', 'My verbose name'),
            (200, 'MY_AGE', 'My verbose age'),
        ])
        assert MY_ENUM.MY_AGE == 100
        assert MY_ENUM[1] == (200, 'My verbose age')
    """

    def __init__(self, enum_list):
        self.enum_list = [(item[0], item[2]) for item in enum_list]
        self.enum_dict = {}
        for item in enum_list:
            self.enum_dict[item[1]] = item[0]

    def __contains__(self, v):
        return (v in self.enum_list)

    def __len__(self):
        return len(self.enum_list)

    def __getitem__(self, v):
        if isinstance(v, basestring):
            return self.enum_dict[v]
        elif isinstance(v, int):
            return self.enum_list[v]

    def __getattr__(self, name):
        return self.enum_dict[name]

    def __iter__(self):
        return self.enum_list.__iter__()

        
EMAIL_TAGS = Enumeration([
    (1, 'TRASH', 'Trashed'),
    (2, 'READ', 'Trashed'),
    (3, 'SPAM', 'Spam'),
    (4, 'IMPORTANT', 'Important'),
    (5, 'QUESTION', 'Question'),
])

class Email(models.Model):
    subject = models.CharField(_(u"Subject"), max_length=255)
    from_name = models.CharField(_(u"From Name"), max_length=50)
    from_email = models.EmailField(_(u"From Email"))
    message = models.TextField(_(u'Message'))
    parent = models.ForeignKey('Email', editable=False, null=True, blank=True, related_name="threads")
    date = models.DateTimeField(auto_now_add=True)
    
    objects = models.Manager()
    emails = EmailManager()
    
    def save(self, force_insert=False, force_update=False, using=None):
        super(Email, self).save(force_insert=force_insert, force_update=force_update, using=using)
        if not self.parent:
            if self.is_question():
                self.tags.create(tag=EMAIL_TAGS.QUESTION)
            
    def is_question(self):
        return "?" in self.message 
    
    @property
    def title(self):
        return "%s - %s" % (self.subject, strip_tags(self.message))[0:65]

    @property
    def respondido(self):
        return self.threads.count() > 0
    
    @property
    def read(self):
        return self.tags.filter(tag=EMAIL_TAGS.READ).count() > 0
    
    @property
    def raw_message(self):
        return strip_tags(self.message)
    
    def mark(self, tag):
        if not self.tags.filter(tag=tag):
            self.tags.create(tag=tag)
        
    def __unicode__(self):
        return self.subject

    class Meta:
        ordering = ('-date',)


class EmailTag(models.Model):
    email = models.ForeignKey(Email, related_name="tags")
    tag = models.PositiveSmallIntegerField(choices=EMAIL_TAGS)
    TAGS = EMAIL_TAGS
    
    class Meta:
        unique_together = ('email', 'tag')
        ordering = ('tag',)