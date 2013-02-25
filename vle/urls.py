from django.conf.urls import patterns, url
from vle.models import Student, Course, Tutor, Session, Subject, Discussion, \
    Ontology, Agent, Log
from vle.views import ObjectListView, ObjectCreateView, ObjectUpdateView, \
    VleIndexView, StudentListView, TutorListView, SubjectListView, CourseListView, \
    SessionListView, DiscussionListView, DiscussionCreateView, OntologyListView, \
    DiscussionThesesToGenerate, DiscussionThesisGenerate, DiscussionUpdateView, \
    OntologyView, AgentMonitor, LogListView, AgentListView, LogRegistry, WSLogList

urlpatterns = patterns('vle',
    url(r'^$', VleIndexView.as_view(), name='home'),
                       
    url(r'^student/$', StudentListView.as_view(model=Student), name='student_list'),
    url(r'^student/add/$', ObjectCreateView.as_view(model=Student), name='student_add'),
    url(r'^student/(?P<pk>\d+)/$', ObjectUpdateView.as_view(model=Student), name='student_change'),
    
    url(r'^tutor/$', TutorListView.as_view(model=Tutor), name='tutor_list'),
    url(r'^tutor/add/$', ObjectCreateView.as_view(model=Tutor), name='tutor_add'),
    url(r'^tutor/(?P<pk>\d+)/$', ObjectUpdateView.as_view(model=Tutor), name='tutor_change'),
    
    url(r'^subject/$', SubjectListView.as_view(model=Subject), name='subject_list'),
    url(r'^subject/add/$', ObjectCreateView.as_view(model=Subject), name='subject_add'),
    url(r'^subject/(?P<pk>\d+)/$', ObjectUpdateView.as_view(model=Subject), name='subject_change'),
    
    url(r'^course/$', CourseListView.as_view(model=Course), name='course_list'),
    url(r'^course/add/$', ObjectCreateView.as_view(model=Course), name='course_add'),
    url(r'^course/(?P<pk>\d+)/$', ObjectUpdateView.as_view(model=Course), name='course_change'),
    
    url(r'^session/$', SessionListView.as_view(model=Session), name='session_list'),
    url(r'^session/add/$', ObjectCreateView.as_view(model=Session), name='session_add'),
    url(r'^session/(?P<pk>\d+)/$', ObjectUpdateView.as_view(model=Session), name='session_change'),
    
    url(r'^ontology/$', OntologyListView.as_view(), name='ontology_list'),
    url(r'^ontology/add/$', ObjectCreateView.as_view(model=Ontology), name='ontology_add'),
    url(r'^ontology/(?P<pk>\d+)/$', ObjectUpdateView.as_view(model=Ontology), name='ontology_change'),
    
    url(r'^discussion/$', DiscussionListView.as_view(), name='discussion_list'),
    url(r'^discussion/add/$', DiscussionCreateView.as_view(), name='discussion_add'),
    url(r'^discussion/(?P<pk>\d+)/$', DiscussionUpdateView.as_view(model=Discussion), name='discussion_change'),
    
    url(r'^log/$', LogListView.as_view(), name='log_list'),
    url(r'^log/add/$', ObjectCreateView.as_view(model=Log), name='log_add'),
    url(r'^log/(?P<pk>\d+)/$', ObjectUpdateView.as_view(model=Log), name='log_change'),
    
    url(r'^agent/$', AgentListView.as_view(), name='agent_list'),
    url(r'^agent/add/$', ObjectCreateView.as_view(model=Agent), name='agent_add'),
    url(r'^agent/(?P<pk>\d+)/$', ObjectUpdateView.as_view(model=Agent), name='agent_change'),
    
    url(r'^discussion/to_generate/$', DiscussionThesesToGenerate.as_view(), name='discussion_to_generate'),
    url(r'^discussion/generate/(?P<pk>\d+)/$', DiscussionThesisGenerate.as_view(), name='discussion_generate'),
    url(r'^ontology/(?P<slug>[-\w]+)/export/$', OntologyView.as_view(), name='ontology_export'),
    
    url(r'^agents/$', AgentMonitor.as_view(), name='agents_monitor'),
    
    url(r'^ws/log/(?P<slug>[-\w]+)/((?P<pk>\d+)/)?$$', WSLogList.as_view(), name='ws_log_list'),
    url(r'^ws/log/add/(?P<slug>[-\w]+)/$', LogRegistry.as_view(), name='ws_log'),
)