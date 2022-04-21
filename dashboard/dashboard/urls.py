from django.conf.urls import url

from dashboard import views

urlpatterns = [url(r'^$',
                   views.contributions, name='contributions'),
               url(r'^me$',
                   views.edit_me, name='edit_me'),
               url(r'^settings$',
                   views.account_settings, name='account_settings'),

               url(r'^contributions/$',
                   views.contributions, name='contributions'),
               url(r'^contribute/$',
                   views.contribute, name='contribute'),

               url(r'^information/(?P<pk>\d+)/$',
                   views.InformationForm.as_view(), name='info_edit'),
               url(r'^event/(?P<pk>\d+)/$',
                   views.EventForm.as_view(), name='info_edit'),
               url(r'^project/(?P<pk>\d+)/$',
                   views.ProjectForm.as_view(), name='info_edit'),
               url(r'^goodpractice/(?P<pk>\d+)/$',
                   views.GoodPracticeForm.as_view(), name='goodpractice_edit'),
               url(r'^usercase/(?P<pk>\d+)/$',
                   views.UserCaseForm.as_view(), name='usercase_edit'),
               url(r'^glossary/(?P<pk>\d+)/$',
                   views.GlossaryForm.as_view(), name='glossary_edit'),
               url(r'^question/(?P<pk>\d+)/$',
                   views.QuestionForm.as_view(), name='question_edit'),

               url(r'^contribute/information/$',
                   views.InformationForm.as_view(), name='info_edit'),
               url(r'^contribute/event/$',
                   views.EventForm.as_view(), name='info_edit'),
               url(r'^contribute/project/$',
                   views.ProjectForm.as_view(), name='info_edit'),
               url(r'^contribute/goodpractice/$',
                   views.GoodPracticeForm.as_view(), name='goodpractice_edit'),
               url(r'^contribute/glossary/$',
                   views.GlossaryForm.as_view(), name='glossary_edit'),
               url(r'^contribute/question/$',
                   views.QuestionForm.as_view(), name='question_edit'),
               url(r'^contribute/usercase/$',
                   views.UserCaseForm.as_view(), name='user_case_edit')
               ]
