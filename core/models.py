from core.converter import tagged_sentence_to_xml, questions_to_aiml, \
    xml_to_tagged_sentence, aiml_to_question
from core.visl import Visl
from django.db import models
from django.db.models.signals import post_init, post_save
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _
from mail.models import Email
from nltk.corpus import stopwords
from util.enum import Enumeration

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
