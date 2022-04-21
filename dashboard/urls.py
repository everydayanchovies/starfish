from django.urls import re_path

from dashboard import views

urlpatterns = [re_path(r'^$',
                       views.contributions, name='contributions'),
               re_path(r'^me$',
                       views.edit_me, name='edit_me'),
               re_path(r'^settings$',
                       views.account_settings, name='account_settings'),

               re_path(r'^contributions/$',
                       views.contributions, name='contributions'),
               re_path(r'^contribute/$',
                       views.contribute, name='contribute'),

               re_path(r'^information/(?P<pk>\d+)/$',
                       views.InformationForm.as_view(), name='info_edit'),
               re_path(r'^event/(?P<pk>\d+)/$',
                       views.EventForm.as_view(), name='info_edit'),
               re_path(r'^project/(?P<pk>\d+)/$',
                       views.ProjectForm.as_view(), name='info_edit'),
               re_path(r'^goodpractice/(?P<pk>\d+)/$',
                       views.GoodPracticeForm.as_view(), name='goodpractice_edit'),
               re_path(r'^usercase/(?P<pk>\d+)/$',
                       views.UserCaseForm.as_view(), name='usercase_edit'),
               re_path(r'^glossary/(?P<pk>\d+)/$',
                       views.GlossaryForm.as_view(), name='glossary_edit'),
               re_path(r'^question/(?P<pk>\d+)/$',
                       views.QuestionForm.as_view(), name='question_edit'),

               re_path(r'^contribute/information/$',
                       views.InformationForm.as_view(), name='info_edit'),
               re_path(r'^contribute/event/$',
                       views.EventForm.as_view(), name='info_edit'),
               re_path(r'^contribute/project/$',
                       views.ProjectForm.as_view(), name='info_edit'),
               re_path(r'^contribute/goodpractice/$',
                       views.GoodPracticeForm.as_view(), name='goodpractice_edit'),
               re_path(r'^contribute/glossary/$',
                       views.GlossaryForm.as_view(), name='glossary_edit'),
               re_path(r'^contribute/question/$',
                       views.QuestionForm.as_view(), name='question_edit'),
               re_path(r'^contribute/usercase/$',
                       views.UserCaseForm.as_view(), name='user_case_edit')
               ]
