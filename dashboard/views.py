from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.forms.models import modelform_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.context_processors import csrf
from django.views import generic
import logging

from django.conf import settings
import dashboard.forms as dforms
import search.forms as sforms
import search.models as models
from search.utils import get_user_communities

SEARCH_SETTINGS = settings.SEARCH_SETTINGS
TAG_REQUEST_MESSAGE = settings.TAG_REQUEST_MESSAGE
ACCOUNT_UPDATED_MSG = settings.ACCOUNT_UPDATED_MSG
ITEM_UPDATED_MSG = settings.ITEM_UPDATED_MSG

logger = logging.getLogger("search")


class QuerySetMock:
    def __init__(self, list, qs):
        self.l = list
        self.qs = qs

    def __getattribute__(self, key):
        if key == "all" or key == "l":
            return super(QuerySetMock, self).__getattribute__(key)
        else:
            qs = super(QuerySetMock, self).__getattribute__("qs")
            return qs.__getattribute__(key)

    def all(self):
        return self.l


def contribute(request):
    return render(
        request,
        "contribute_options.html",
        {
            "user_communities": get_user_communities(request.user),
            "user_case_permission": request.user.has_perm("search.add_usercase")
            or request.user.is_superuser,
        },
    )


def contributions(request):
    if not request.user.is_authenticated:
        # TODO: usability
        return HttpResponse("Please log in.")

    person = models.Person.objects.get(user=request.user)

    if request.user.is_superuser:
        conts = {
            "goodpractice": models.GoodPractice.objects.order_by("title").distinct(),
            "information": models.Information.objects.order_by("title").distinct(),
            "project": models.Project.objects.order_by("title").distinct(),
            "event": models.Event.objects.order_by("title").distinct(),
            "question": models.Question.objects.order_by("title").distinct(),
            "glossary": models.Glossary.objects.order_by("title").distinct(),
            "usercase": models.UserCase.objects.order_by("title").distinct(),
        }
    else:
        collab = models.ItemAuthor.objects.filter(
            person=person, status="ACCEPTED"
        ).values_list("item", flat=True)

        conts = {
            "goodpractice": models.GoodPractice.objects.filter(
                Q(authors=person) | Q(id__in=collab)
            )
            .order_by("title")
            .distinct(),
            "information": models.Information.objects.filter(
                Q(authors=person) | Q(id__in=collab)
            )
            .order_by("title")
            .distinct(),
            "project": models.Project.objects.filter(
                Q(authors=person) | Q(id__in=collab)
            )
            .order_by("title")
            .distinct(),
            "event": models.Event.objects.filter(Q(authors=person) | Q(id__in=collab))
            .order_by("title")
            .distinct(),
            "question": models.Question.objects.filter(
                Q(authors=person) | Q(id__in=collab)
            )
            .order_by("title")
            .distinct(),
            "glossary": models.Glossary.objects.filter(
                Q(authors=person) | Q(id__in=collab)
            )
            .order_by("title")
            .distinct(),
            "usercase": models.UserCase.objects.filter(
                Q(authors=person) | Q(id__in=collab)
            )
            .order_by("title")
            .distinct(),
        }

    return render(
        request,
        "contributions.html",
        {
            "user_communities": get_user_communities(request.user),
            "contributions": conts,
        },
    )


def edit_me(request):
    if not request.user.is_authenticated:
        # TODO: usability
        return HttpResponse("Please log in.")

    person = models.Person.objects.get(user=request.user)

    PersonForm = modelform_factory(
        models.Person,
        fields=("headline", "email", "website", "public_email", "about", "photo"),
    )

    context = {
        "user_communities": get_user_communities(request.user),
        "form": PersonForm(instance=person),
        "person": person,
        "syntax": SEARCH_SETTINGS["syntax"],
    }

    if request.method != "POST":
        return render(
            request,
            "dashboard_person.html",
            context,
        )

    # TODO: check if this also affects the person in context so that we can easily reuse that when we return.
    # Same for other functions here
    if request.FILES.get("photo"):
        person.photo = request.FILES.get("photo")
        person.save()

    form = PersonForm(request.POST, instance=person)
    if form.is_valid():
        form.save()

    messages.add_message(request, messages.INFO, ACCOUNT_UPDATED_MSG.format("profile"))

    return render(
        request,
        "dashboard_person.html",
        {
            "user_communities": get_user_communities(request.user),
            "form": form,
            "person": person,
            "syntax": SEARCH_SETTINGS["syntax"],
        },
    )


def account_settings(request):
    if not request.user.is_authenticated:
        # TODO: usability.
        return HttpResponse("Please log in.")

    person = models.Person.objects.get(user=request.user)
    emailform = dforms.ChangeEmailForm(request.POST)
    passwordform = dforms.ChangePasswordForm(request.POST)

    if request.method != "POST":
        return render(
            request,
            "account_settings.html",
            {
                "emailform": dforms.ChangeEmailForm(),
                "passwordform": dforms.ChangePasswordForm(),
                "person": person,
                "syntax": SEARCH_SETTINGS["syntax"],
            },
        )

    if emailform.is_valid():
        email = emailform.cleaned_data["newemail"]
        if email:
            person.email = email
            messages.add_message(
                request,
                messages.INFO,
                ACCOUNT_UPDATED_MSG.format("email adddress"),
            )

    if passwordform.is_valid():
        newpwd = passwordform.cleaned_data["newpassword"]
        if newpwd:
            u = request.user
            u.set_password(newpwd)
            u.save()
            messages.add_message(
                request, messages.INFO, ACCOUNT_UPDATED_MSG.format("password")
            )

    return render(
        request,
        "account_settings.html",
        {
            "emailform": emailform,
            "passwordform": passwordform,
            "person": person,
            "syntax": SEARCH_SETTINGS["syntax"],
        },
    )


class EditForm(generic.View):
    success_url = "/dashboard/"

    def get(self, request, *args, **kwargs):
        """Get a form for a new or existing Object."""

        if not request.user.is_authenticated:
            # TODO: usability
            return HttpResponse("Please log in.")

        if request.user.person.draft:
            return render(request, "no_access.html")

        # Communities
        user_communities = get_user_communities(request.user)
        communities = models.Community.objects.filter(
            pk__in=[c.id for c in user_communities]
        )

        # Existing object
        elems = request.path.strip("/").split("/")
        try:
            obj_id = int(elems[2])
            obj = get_object_or_404(self.model_class, pk=obj_id)
            collaborators = models.ItemAuthor.objects.filter(
                status="ACCEPTED", item=obj
            )
            authors = {a.person for a in obj.authors.all()} | {
                c.person for c in collaborators
            }

            if (
                request.user not in [a.user for a in authors]
                and not request.user.is_superuser
            ):
                return render(request, "no_access.html")

            form = self.form_class(instance=obj, communities=communities)
            c = {
                "obj": obj,
                "authors": authors,
                "links": models.Item.objects.order_by("type"),
                "all_communities": models.Community.objects.all(),
                "form_communities": communities,
                "user_communities": user_communities,
                "form": form,
            }

            if self.model_class == models.UserCase:
                c["wallpaper_url"] = obj.wallpaper

        except ValueError:
            if self.model_class == models.UserCase:
                form = self.form_class(
                    {
                        "text": models.get_template(self.model_class),
                        "context_goals": "<h2>Local context (specific)</h2><br /><h2>Local CPD goals</h2>",
                        "cpd_activities": "<h2>CPD activities at the local university</h2><br /><h2>Teaching and learning materials</h2><br /><h2>Sustainable implementation</h2>",
                        "evaluation": "<h2>Expected impact of the CPD User Case</h2><br /><h2>Plans for eventual continuation of the CPD within the same topic</h2>",
                    },
                    communities=communities,
                )
            else:
                form = self.form_class(
                    {"text": models.get_template(self.model_class)},
                    communities=communities,
                )

            c = {
                "links": models.Item.objects.order_by("type"),
                "form": form,
                "all_communities": models.Community.objects.all(),
                "form_communities": communities,
                "user_communities": user_communities,
                "is_new": True,
            }

        c.update(csrf(request))
        # renderer=form.renderer
        return render(
            request,
            self.template_name,
            c,
        )

    def post(self, request, *args, **kwargs):
        """Post a new object or update existing"""

        if not request.user.is_authenticated:
            return HttpResponse("Please log in.")

        # Communities
        user_communities = get_user_communities(request.user)
        communities = models.Community.objects.filter(
            pk__in=[c.id for c in user_communities]
        )

        # Existing object
        elems = request.path.strip("/").split("/")
        post_v = request.POST.copy()
        post_v["authors"] = [request.user.person.id]

        try:
            obj_id = int(elems[-1])
            obj = get_object_or_404(self.model_class, pk=obj_id)
            if authors := obj.authors.all():
                post_v["authors"] = [a.id for a in authors]
            form = self.form_class(post_v, instance=obj, communities=communities)
        except ValueError:  # New object
            form = self.form_class(post_v, communities=communities)

        # for the future developer, django is very weird and will
        # silently change [1, 2, 3] to [[1, 2, 3]]
        # this reverts that change
        form.data.setlist("authors", form.data["authors"])

        if form.is_valid():
            # TODO: this validation was broken
            # Check if all tags are already known
            # tag_str = form.data.get("tags", None)
            # if tag_str:
            #     tags, unknown_tags = parse_tags(tag_str)
            #     if (unknown_tags["token"]
            #         or unknown_tags["person"]
            #         or unknown_tags["literal"]):
            #         print(unknown_tags)
            #         messages.info(request, TAG_REQUEST_MESSAGE)
            if self.success_url[-1] == "/":
                obj = form.save(commit=False)
                obj.save()
                obj_id = str(obj.pk)
                links = form.cleaned_data.get("links")
                for link in links:
                    obj.link(link)
                del form.cleaned_data["links"]
                form.save_m2m()
            else:
                obj = form.save(commit=False)
                obj.save()
                obj_id = "/" + str(obj.pk)
                links = form.cleaned_data.get("links")
                for link in links:
                    obj.link(link)
                del form.cleaned_data["links"]
                # TODO: check if this is a security issue.
                print(obj.tags.all())
                print(obj)
                # form.cleaned_data["tags"] = obj.tags.all()

                form.save_m2m()
            redirect = self.success_url + obj_id

            messages.add_message(
                request,
                messages.INFO,
                ITEM_UPDATED_MSG.format(self.model_class.__name__),
            )
            return HttpResponseRedirect(redirect)
        else:
            return render(
                request,
                self.template_name,
                {"user_communities": user_communities, "form": form},
            )


class InformationForm(EditForm):
    template_name = "information_form.html"
    form_class = sforms.EditInformationForm
    model_class = models.Information
    success_url = "/dashboard/information"


class GoodPracticeForm(EditForm):
    template_name = "goodpractice_form.html"
    form_class = sforms.EditGoodPracticeForm
    model_class = models.GoodPractice
    success_url = "/dashboard/goodpractice"


class EventForm(EditForm):
    template_name = "event_form.html"
    form_class = sforms.EditEventForm
    model_class = models.Event
    success_url = "/dashboard/event"


class ProjectForm(EditForm):
    template_name = "project_form.html"
    form_class = sforms.EditProjectForm
    model_class = models.Project
    success_url = "/dashboard/project"


class QuestionForm(EditForm):
    template_name = "question_form.html"
    form_class = sforms.EditQuestionForm
    model_class = models.Question
    success_url = "/dashboard/question"


class UserCaseForm(PermissionRequiredMixin, EditForm):
    permission_required = ["search.add_usercase"]
    template_name = "user_case_form.html"
    form_class = sforms.EditUserCaseForm
    model_class = models.UserCase
    success_url = "/dashboard/usercase"

    def post(self, request, *args, **kwargs):
        # logger.info("logging:", CPDQuestion._meta.verbose_name_plural, Link._meta.verbose_name_plural, Community._meta.verbose_name_plural)

        if request.POST.get("title"):
            match = models.UserCase.objects.filter(title=request.POST.get("title"))
            if len(match) == 1 and request.FILES.get("wallpaper"):
                match[0].wallpaper = request.FILES.get("wallpaper")
                match[0].save()

        return super().post(request, args, kwargs)


class GlossaryForm(EditForm):
    template_name = "glossary_form.html"
    form_class = sforms.EditGlossaryForm
    model_class = models.Glossary
    success_url = "/dashboard/glossary"
