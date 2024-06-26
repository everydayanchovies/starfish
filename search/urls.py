from django.conf import settings
from django.urls import re_path, path
from django.conf.urls import include
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

from search import views, apis

urlpatterns = [
    re_path(r"^$", views.search, name="index"),
    re_path(r"^privacy-policy$", views.privacy_policy, name="privacy-policy"),
    re_path(r"^terms-of-use$", views.terms_of_service, name="terms-of-service"),
    re_path(r"^validate$", views.validate_profiles, name="validate"),
    # re_path(r'^validate/accept$',
    #         views.validate_accept, name='validate_accept'),
    # re_path(r'^validate/reject$',
    #         views.validate_reject, name='validate_reject'),
    re_path(r"^invitation/accept$", views.accept_invitation, name="invitation-accept"),
    re_path(
        r"^invitation/decline$", views.decline_invitation, name="invitation-decline"
    ),
    re_path(r"^autocomplete$", views.autocomplete, name="autocomplete"),
    re_path(r"^search", views.search_list, name="search"),
    re_path(r"^browse", views.browse, name="browse"),
    re_path(r"^analytics", views.analytics, name="analytics"),
    re_path(r"^feedback", views.feedback, name="feedback"),
    re_path(r"^tag/(?P<handle>.+)/$", views.tag, name="tag"),
    re_path(r"^person/(?P<pk>\d+)/$", views.person, name="person"),
    # Infos
    re_path(
        r"^information/(?P<pk>\d+)/$", views.InformationView.as_view(), name="info"
    ),
    re_path(r"^event/(?P<pk>\d+)/$", views.EventView.as_view(), name="info"),
    re_path(r"^project/(?P<pk>\d+)/$", views.ProjectView.as_view(), name="info"),
    re_path(
        r"^goodpractice/(?P<pk>\d+)/$",
        views.GoodPracticeView.as_view(),
        name="goodpractice",
    ),
    re_path(r"^glossary/(?P<pk>\d+)/$", views.GlossaryView.as_view(), name="glossary"),
    re_path(r"^question/(?P<pk>\d+)/$", views.QuestionView.as_view(), name="question"),
    re_path(r"^usercase/(?P<pk>\d+)/$", views.UserCaseView.as_view(), name="usercase"),
    re_path(
        r"^invite-collaborator$", views.invite_collaborator, name="invitecollaborator"
    ),
    re_path(r"^loadquestionform$", views.loadquestionform, name="loadquestionform"),
    re_path(r"^submitquestion$", views.submitquestion, name="submitquestion"),
    re_path(r"^comment$", views.comment, name="comment"),
    re_path(r"^vote$", views.cast_vote, name="cast_vote"),
    re_path(r"^api/comment$", apis.comment, name="api_comment"),
    re_path(r"^register", views.register_user, name="register"),
    re_path(r"^login", views.login_user, name="login"),
    re_path(r"^logout", views.logout_user, name="logout"),
    path(
        "password-reset/",
        PasswordResetView.as_view(
            template_name="password-reset/reset.html",
            html_email_template_name="password-reset/email.html",
        ),
        name="password-reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(template_name="password-reset/done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(template_name="password-reset/confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        PasswordResetCompleteView.as_view(template_name="password-reset/complete.html"),
        name="password_reset_complete",
    ),
    re_path(r"ivoauth_debug$", views.ivoauth_debug, name="ivoauth_debug"),
    re_path(
        r"ivoauth/debug_callback",
        views.ivoauth_debug_callback,
        name="ivoauth_debug_callback",
    ),
    re_path(r"ivoauth/callback", views.ivoauth_callback, name="ivoauth_callback"),
    re_path(r"ivoauth$", views.ivoauth, name="ivoauth"),
]
