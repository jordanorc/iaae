# -*- coding: utf-8 -*-
from django.db import models
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import unescape_entities
from django.utils.translation import ugettext_lazy as _
from util.enum import Enumeration
from django.core.exceptions import ValidationError
from mail.converter import tagged_sentence_to_xml, questions_to_aiml, \
    xml_to_tagged_sentence, aiml_to_question
from util.visl import Visl
from django.db.models.signals import post_init, post_save
from django.dispatch.dispatcher import receiver
from nltk.corpus import stopwords

EMAIL_TAGS = Enumeration([
    (1, 'TRASH', 'Trashed'),
    (2, 'READ', 'Trashed'),
    (3, 'SPAM', 'Spam'),
    (4, 'IMPORTANT', 'Important'),
    (5, 'QUESTION', 'Question'),
    (6, 'REPLIED', 'Replied'),
])

class EmailManager(models.Manager):
    
    def get_query_set(self):
        queryset = super(EmailManager, self).get_query_set()
        queryset = queryset.filter(parent__isnull=True).exclude(tags__tag__in=(EMAIL_TAGS.TRASH,))
        return queryset
    
    def unreplied(self):
        return self.get_query_set().exclude(tags__tag=EMAIL_TAGS.REPLIED)

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
        else:
            self.parent.tags.create(tag=EMAIL_TAGS.REPLIED)
            
    def clean(self):
        if self.parent:
            #force unique response
            if self.parent.threads.count() > 0:
                raise ValidationError(_(u'There is already a reply to this email'))    
          
    def is_question(self):
        return "?" in self.message 
    
    @property
    def title(self):
        return mark_safe("%s - %s" % (self.subject, strip_tags(self.message))[0:65])

    @property
    def respondido(self):
        return self.threads.count() > 0
    
    @property
    def read(self):
        return self.tags.filter(tag=EMAIL_TAGS.READ).count() > 0
    
    @property
    def raw_message(self):
        return strip_tags(unescape_entities(self.message))
    
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
        
        

'''
E-mail processing
'''
EMAIL_DATA = Enumeration([
    (1, 'AIML', 'AIML Template'),
    (2, 'TAGS', 'Tagged Sentence'),
])

# Create your models here.
class EmailData(models.Model):
    
    email = models.ForeignKey(Email, related_name="data")
    data_type = models.PositiveSmallIntegerField(choices=EMAIL_DATA)
    data = models.TextField()
    
    class Meta:
        unique_together = ('email', 'data_type')


@receiver(post_init, sender=Email)
def set_email_data(sender, **kwargs):

    email = kwargs["instance"]
    
    if email.pk and not email.parent:
        email.tagged_sentences = xml_to_tagged_sentence(email)
        email.aiml = aiml_to_question(email)
        
        filtered_message = email.raw_message.split(" ") #make a copy of the word_list
        for key, word in enumerate(filtered_message): # iterate over word_list
            if word in stopwords.words('portuguese'): 
                filtered_message[key] = "*"
        email.filtered_message = " ".join(filtered_message)
    

@receiver(post_save, sender=Email)
def collect_email_data(sender, **kwargs):
   
    email = kwargs["instance"]
    
    if not email.parent:
        visl = Visl()
        tagged_sentence = visl.tag(email.raw_message)
        
        xml = tagged_sentence_to_xml(tagged_sentence)
        data = EmailData.objects.create(email=email, data_type=EMAIL_DATA.TAGS, data=xml)
    else:
        filtered_message = email.parent.raw_message.split(" ") #make a copy of the word_list
        for key, word in enumerate(filtered_message): # iterate over word_list
            if word in stopwords.words('portuguese'): 
                filtered_message[key] = "*"
                
        aiml = questions_to_aiml([(" ".join(filtered_message), email.raw_message)])
        data = EmailData.objects.create(email=email.parent, data_type=EMAIL_DATA.AIML, data=aiml)