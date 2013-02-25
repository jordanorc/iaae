from django.contrib.auth.models import User, Group
from django.db import models, models
from django.template.defaultfilters import slugify
from django.utils.timezone import now
from django.utils.translation import ugettext as _
import os
import string

class Student(models.Model):
    GENDER_CHOICES = (
        (1, _(u'Male')),
        (2, _(u'Female')),
    )
    
    first_name = models.CharField(_(u"first name"), max_length=20)
    middle_name = models.CharField(_(u"middle name"), max_length=20)
    last_name = models.CharField(_(u"last name"), max_length=20)
    date_birth = models.DateField(_(u"date of birth"))
    gender = models.PositiveSmallIntegerField(_(u"gender"), choices=GENDER_CHOICES)
    
    address_line1 = models.CharField(_(u"address line1"), max_length=50, null=True, blank=True)
    address_line2 = models.CharField(_(u"address line2"), max_length=50, null=True, blank=True)
    city = models.CharField(_(u"city"), max_length=50, null=True, blank=True)
    state = models.CharField(_(u"state"), max_length=50, null=True, blank=True)
    pin_code = models.CharField(_(u"pin code"), max_length=10, null=True, blank=True)
    country = models.CharField(_(u"country"), max_length=50, null=True, blank=True)
    
    user = models.ForeignKey(User, editable=True)
    
    def __unicode__(self):
        return "%s %s %s" % (self.first_name, self.middle_name, self.last_name)
    
    class Meta:
        verbose_name = ('student')
        verbose_name_plural = ('students')

class Tutor(models.Model):
    GENDER_CHOICES = (
        (1, _(u'Male')),
        (2, _(u'Female')),
    )
    
    first_name = models.CharField(_(u"first name"), max_length=20)
    middle_name = models.CharField(_(u"middle name"), max_length=20)
    last_name = models.CharField(_(u"last name"), max_length=20)
    date_birth = models.DateField(_(u"date of birth"))
    gender = models.PositiveSmallIntegerField(_(u"gender"), choices=GENDER_CHOICES)
    
    address_line1 = models.CharField(_(u"address line1"), max_length=50, null=True, blank=True)
    address_line2 = models.CharField(_(u"address line2"), max_length=50, null=True, blank=True)
    city = models.CharField(_(u"city"), max_length=50, null=True, blank=True)
    state = models.CharField(_(u"state"), max_length=50, null=True, blank=True)
    pin_code = models.CharField(_(u"pin code"), max_length=10, null=True, blank=True)
    country = models.CharField(_(u"country"), max_length=50, null=True, blank=True)
    
    user = models.ForeignKey(User, editable=True)
    
    def __unicode__(self):
        return "%s %s %s" % (self.first_name, self.middle_name, self.last_name)
    
    class Meta:
        verbose_name = ('tutor')
        verbose_name_plural = ('tutors')
        
class Subject(models.Model):
    name = models.CharField(max_length=70)
    
    def __unicode__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=70)
    slug = models.SlugField()
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = ('course')
        verbose_name_plural = ('courses')
        
def generate_years_choice():
    actual_year = now().year
    return [(year, str(year)) for year in range(actual_year-5, actual_year+1)]

class Session(models.Model):
    course = models.ForeignKey(Course)
    slug = models.CharField(max_length=50, blank=True)
    
    semester = models.IntegerField(choices=((1, 'Fisrt Semester'), (2, 'Second Semester')))
    year = models.IntegerField('Year', choices=generate_years_choice())
    date_from = models.DateField()
    date_to = models.DateField()
    students = models.ManyToManyField(Student, null=True, blank=True, related_name='sessions')
    tutors = models.ManyToManyField(Tutor, null=True, blank=True, related_name=_('Tutor courses'))
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.course.name)
        super(Session, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.course.name
    
    class Meta:
        verbose_name = ('session')
        verbose_name_plural = ('sessions')
        
class Discussion(models.Model):
    title = models.CharField(max_length=200)
    session = models.ForeignKey(Session)    
    students = models.ManyToManyField(Student)
    number_theses = models.PositiveIntegerField()
    
    class Meta:
        verbose_name = ('discussion')
        verbose_name_plural = ('discussions')
        
class Thesis(models.Model):
    description = models.CharField(max_length=200, verbose_name=_(u"Thesis"))
    discussion = models.ForeignKey(Discussion, related_name="theses", editable=False)
    valid = models.BooleanField(_(u"Is true"))   
    
    class Meta:
        verbose_name = ('thesis')
        verbose_name_plural = ('theses')
        
class Ontology(models.Model):
    name = models.CharField(max_length=200, verbose_name=_(u"Name"))
    slug = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=200, verbose_name=_(u"Description"), blank=True, null=True)
    file = models.FileField(upload_to="ontologies")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Ontology, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = ('ontology')
        verbose_name_plural = ('ontologies')
        
        
class Log(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    
    class Meta:
        verbose_name = ('log')
        verbose_name_plural = ('logs')
        
class Agent(models.Model):
    slug = models.SlugField(max_length=50)
    key = models.CharField(blank=True, max_length=20)
    logs = models.ManyToManyField(Log, blank=True, editable=False)
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_random_string(20)
        return super(Agent, self).save(*args, **kwargs)

    def generate_random_string(self, length, stringset=string.ascii_letters+string.digits+string.punctuation):
        return ''.join([stringset[i%len(stringset)] \
            for i in [ord(x) for x in os.urandom(length)]])