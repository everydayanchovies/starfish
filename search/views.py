import itertools
import json
import logging
import random
from builtins import str
from urllib.error import HTTPError
from urllib.parse import urlencode, quote
from urllib.request import urlopen

import ldap
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import EmailMultiAlternatives
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseBadRequest,
    HttpResponseNotFound,
)
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from search import retrieval
from search import utils
from search.forms import *
from search.models import *
from search.widgets import *

from zpython import *

SEARCH_SETTINGS = settings.SEARCH_SETTINGS
LOGIN_REDIRECT_URL = settings.LOGIN_REDIRECT_URL
HOSTNAME = settings.HOSTNAME
ITEM_TYPES = settings.ITEM_TYPES
IVOAUTH_TOKEN = settings.IVOAUTH_TOKEN
IVOAUTH_URL = settings.IVOAUTH_URL
ADMIN_NOTIFICATION_EMAIL = settings.ADMIN_NOTIFICATION_EMAIL
QUESTION_ASKED_TEXT = settings.QUESTION_ASKED_TEXT
COMMENT_PLACED_TEXT = settings.COMMENT_PLACED_TEXT

MAX_AUTOCOMPLETE = 5
logger = logging.getLogger("search")


def check_profile_completed(func):
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.person.about == "":
            messages.add_message(
                request,
                50,
                "<a href='%s'>Click here to complete your profile</a>"
                % (reverse("edit_me")),
            )
        return func(request, *args, **kwargs)

    return inner


def sorted_tags(tags):
    p, t, c, o = [], [], [], []

    try:
        for tag in tags:
            if tag["type"] == "P":
                p.append(tag)
            elif tag["type"] == "T":
                t.append(tag)
            elif tag["type"] == "C":
                c.append(tag)
            elif tag["type"] == "O":
                o.append(tag)
        p.sort(key=lambda x: x["handle"])
        t.sort(key=lambda x: x["handle"])
        c.sort(key=lambda x: x["handle"])
        o.sort(key=lambda x: x["handle"])

    except TypeError:
        for tag in tags:
            if tag.type == "P":
                p.append(tag)
            elif tag.type == "T":
                t.append(tag)
            elif tag.type == "C":
                c.append(tag)
            elif tag.type == "O":
                o.append(tag)
        p.sort(key=lambda x: x.handle)
        t.sort(key=lambda x: x.handle)
        c.sort(key=lambda x: x.handle)
        o.sort(key=lambda x: x.handle)

    return {"p": p, "t": t, "c": c, "o": o}


def editcontent(request, pk):
    item = get_object_or_404(Items, pk=pk)
    form = EditInformationForm(instance=item.downcast())
    context = {"form", form}
    return render(request, "edit.html", context)


def person(request, pk):
    person = get_object_or_404(Person, id=pk)
    user_communities = set(utils.get_user_communities(request.user))

    context = sorted_tags(person.tags.all())
    context["user_communities"] = user_communities
    # Filter links for communities
    links = filter(
        lambda x: len(set(x.communities.all()) & user_communities) > 0,
        person.links.all(),
    )

    # Remove events that have already passed
    links = set(
        filter(lambda x: not x.downcast().is_past_due if x.type == "E" else True, links)
    )

    context["community_links"] = links
    context["person"] = person
    context["syntax"] = SEARCH_SETTINGS["syntax"]
    context["next"] = person.get_absolute_url()
    return render(request, "person.html", context)


class StarfishDetailView(generic.DetailView):
    def get_context_data(self, **kwargs):
        context = super(StarfishDetailView, self).get_context_data(**kwargs)

        user_communities = set(utils.get_user_communities(self.request.user))
        context["user_communities"] = user_communities

        def links_filter(link):
            if len(set(link.communities.all()) & user_communities) == 0:
                return False
            if link.type == "E" and link.downcast().is_past_due:
                return False
            if link.type == "P" and link.dict_format()["is_ghost"]:
                return False
            return True

        # Filter links for communities
        context["community_links"] = set(
            filter(links_filter, self.get_object().links.all())
        )

        return context

    def get_object(self, queryset=None):
        o = super().get_object(queryset=queryset)

        # TODO: test this
        for author in [a for a in o.authors.all() if a.is_ghost]:
            author.handle = "john.dee"
            author.name = "John Dee"
            author.email = "johndee@example.com"
            author.id = 1

        return o


class InformationView(StarfishDetailView):
    model = Information
    template_name = "info.html"

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get a context
        context = super(InformationView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["syntax"] = SEARCH_SETTINGS["syntax"]
        context["next"] = self.object.get_absolute_url()
        context["search"] = None
        context["summaries"] = []

        def get_summary(tag):
            try:
                # page_info = wikipedia.page(tag.handle, auto_suggest=True, redirect=True)
                # url = "https://en.wikipedia.org/?curid=" + page_info.pageid

                tag_dict = tag.dict_format()
                summary = (
                    tag_dict["summary"]
                    if not tag_dict["info"]
                    else tag_dict["info"]["summary"]
                )
                return {
                    "tag_dict": tag.dict_format(),
                    "tag": tag.handle,
                    "raw_tag": tag,
                    "summary": summary,  # wikipedia.summary(tag.handle, sentences=1),
                    "title": tag.handle,
                    "url": tag.info_link,
                }
            except:
                return {
                    "tag_dict": tag.dict_format(),
                    "tag": tag.handle,
                    "raw_tag": tag,
                    "summary": "No summary available",
                    "title": tag.handle,
                    "url": None,
                }

        for tag in self.object.tags.all():

            if tag.type == "D":
                continue

            context["summaries"].append(get_summary(tag))

        # Fetch tags and split them into categories
        context.update(sorted_tags(self.object.tags.all()).items())
        return context


class GoodPracticeView(InformationView):
    model = GoodPractice

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GoodPracticeView, self).get_context_data(**kwargs)
        context["information"] = context["goodpractice"]
        return context


class UserCaseView(InformationView):
    model = UserCase
    template_name = "user_case.html"


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UserCaseView, self).get_context_data(**kwargs)

        context["information"] = context["usercase"]
        if (context["information"].get_cpd_scenario()):
            context["competences_list"] = list(dict.fromkeys(context["information"].get_cpd_scenario().scales_competences))
            context["attitudes_list"] = list(dict.fromkeys(context["information"].get_cpd_scenario().scales_attitudes))
            context["activities_list"] = list(dict.fromkeys(context["information"].get_cpd_scenario().scales_activities))

        return context


class EventView(StarfishDetailView):
    model = Event
    template_name = "event.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(EventView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["syntax"] = SEARCH_SETTINGS["syntax"]
        # Fetch tags and split them into categories
        p, t, c, o = [], [], [], []
        for tag in self.object.tags.all():
            if tag.type == "P":
                p.append(tag)
            elif tag.type == "T":
                t.append(tag)
            elif tag.type == "C":
                c.append(tag)
            elif tag.type == "O":
                o.append(tag)
        context["p"] = p
        context["t"] = t
        context["c"] = c
        context["o"] = o
        context["next"] = self.object.get_absolute_url()

        return context


class ProjectView(StarfishDetailView):
    model = Project
    template_name = "project.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProjectView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["syntax"] = SEARCH_SETTINGS["syntax"]
        # Fetch tags and split them into categories
        p, t, c, o = [], [], [], []
        for tag in self.object.tags.all():
            if tag.type == "P":
                p.append(tag)
            elif tag.type == "T":
                t.append(tag)
            elif tag.type == "C":
                c.append(tag)
            elif tag.type == "O":
                o.append(tag)
        context["p"] = p
        context["t"] = t
        context["c"] = c
        context["o"] = o
        context["next"] = self.object.get_absolute_url()

        return context


class QuestionView(StarfishDetailView):
    model = Question
    template_name = "question.html"

    def get_context_data(self, *args, **kwargs):
        # Call the base implementation first to get a context
        context = super(QuestionView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["syntax"] = SEARCH_SETTINGS["syntax"]
        # Fetch tags and split them into categories
        p, t, c, o = [], [], [], []
        for tag in self.object.tags.all():
            if tag.type == "P":
                p.append(tag)
            elif tag.type == "T":
                t.append(tag)
            elif tag.type == "C":
                c.append(tag)
            elif tag.type == "O":
                o.append(tag)
        context["p"] = p
        context["t"] = t
        context["c"] = c
        context["o"] = o
        context["next"] = self.object.get_absolute_url()
        context["form"] = CommentForm(
            initial={"item_type": self.object.type, "item_id": self.object.id}
        )
        return context


class GlossaryView(StarfishDetailView):
    model = Glossary
    template_name = "glossary.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossaryView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["syntax"] = SEARCH_SETTINGS["syntax"]
        context["next"] = self.object.get_absolute_url()
        context["information"] = context["glossary"]

        try:
            # Fetch tag that is exlained by this
            tag = Tag.objects.get(glossary=context["object"])
        except (Tag.DoesNotExist, Tag.MultipleObjectsReturned):
            context["search"] = None
        else:
            context["search"] = tag
            aliases = list(Tag.objects.filter(alias_of=tag))
            if len(aliases) > 0:
                context["aliases"] = ", ".join([alias.handle for alias in aliases])
            else:
                context["aliases"] = None

        # Fetch tags and split them into categories
        context.update(sorted_tags(self.object.tags.all()).items())
        return context


@login_required
def invite_collaborator(request):
    if request.method == "POST":
        person = Person.objects.filter(email=request.POST["invitee"])
        if request.POST["type"] == "G":
            item = GoodPractice.objects.get(id=request.POST["id"])
        elif request.POST["type"] == "U":
            item = UserCase.objects.get(id=request.POST["id"])
        elif request.POST["type"] == "I":
            item = Information.objects.get(id=request.POST["id"])
        elif request.POST["type"] == "R":
            item = Project.objects.get(id=request.POST["id"])
        elif request.POST["type"] == "E":
            item = Event.objects.get(id=request.POST["id"])
        elif request.POST["type"] == "S":
            item = Glossary.objects.get(id=request.POST["id"])
        elif request.POST["type"] == "Q":
            item = Question.objects.get(id=request.POST["id"])
        else:
            return HttpResponseBadRequest()

        if person.exists():
            ItemAuthor(person=person.first(), item=item).save()

        return HttpResponse()

    return HttpResponseBadRequest()


def login_user(request):
    errors = []
    username = password = redirect_url = ""
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        redirect_url = request.POST.get("next", "/")
        print("FORM email", email)
        user = authenticate(username=email, password=password)

        if user is not None and user.is_active:
            login(request, user)

            # Check if redirecturl valid
            if "//" in redirect_url and re.match(r"[^\?]*//", redirect_url):
                redirect_url = LOGIN_REDIRECT_URL
            return redirect(redirect_url)
        if user is None:
            errors += ["Invalid email and password combination!"]

    form = LoginForm()

    return render(request, "login.html", {"form": form, "errors": errors})


def register_user(request):
    errors = []
    username = password = redirect_url = ""
    if request.method == "POST":
        handle = request.POST["handle"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        passwordc = request.POST["passwordc"]
        university = request.POST["university"]
        introduction = request.POST.get("introduction", "")

        handle_match = Person.objects.filter(handle=handle)
        email_match = Person.objects.filter(email=email)

        if handle_match.exists():
            errors += ["Handle is already taken"]

        if email_match.exists():
            errors += ["Email is already registered"]

        if passwordc != password:
            errors += ["Passwords don't match"]

        if len(password) < 8:
            errors += ["Password must be at least 8 characters"]

        if len(errors) == 0:
            user = User.objects.create_user(
                username=handle,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )
            user.save()

            pub_com, _ = Community.objects.get_or_create(name="Public")

            person = Person.objects.create(
                handle=handle,
                email=email,
                user=user,
                name=first_name + " " + last_name,
                university=university,
                introduction=introduction,
            )
            person.communities.add(pub_com)
            person.save()

            redirect_url = request.POST.get("next", "/login")
            return redirect(redirect_url)

    form = RegisterForm()

    return render(request, "register.html", {"form": form, "errors": errors})


def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")


def ivoauth(request):
    callback_url = (
        str(request.build_absolute_uri("ivoauth/callback")) + "/?ticket={#ticket}"
    )
    post_data = [("token", IVOAUTH_TOKEN), ("callback_url", callback_url)]
    try:
        content = json.loads(
            urlopen(IVOAUTH_URL + "/ticket", urlencode(post_data).encode("utf-8"))
            .read()
            .decode("utf-8")
        )
    except HTTPError:
        logger.error("Invalid url")
        return HttpResponseBadRequest()
    if content["status"] == "success":
        logger.debug("IVO authentication successful")
        return HttpResponseRedirect(IVOAUTH_URL + "/login/" + content["ticket"])
    else:
        logger.debug("IVO authentication failed")
    return HttpResponseBadRequest()


def ivoauth_debug(request):
    callback_url = (
        str(request.build_absolute_uri("ivoauth/debug_callback")) + "/?ticket={#ticket}"
    )
    post_data = [("token", IVOAUTH_TOKEN), ("callback_url", callback_url)]
    try:
        content = json.loads(
            urlopen(
                IVOAUTH_URL + "/ticket", urlencode(post_data).encode("utf-8")
            ).decode("utf-8")
        )
    except HTTPError:
        logger.error("Invalid url")
        return HttpResponseBadRequest()
    if content["status"] == "success":
        logger.debug("IVO authentication successful")
        return HttpResponseRedirect(IVOAUTH_URL + "/login/" + content["ticket"])
    else:
        logger.debug("IVO authentication failed")
    return HttpResponseBadRequest()


def ivoauth_debug_callback(request):
    # Retrieve ticket given by ivoauth and use it
    ticket = request.GET.get("ticket", "")
    if not ticket:
        logger.error("no ticket")
    url = IVOAUTH_URL + "/status"
    post_data = [("token", IVOAUTH_TOKEN), ("ticket", ticket)]
    try:
        content = (
            urlopen(url, urlencode(post_data).encode("utf-8")).read().decode("utf-8")
        )
    except HTTPError:
        logger.error("Invalid url")
        return HttpResponseBadRequest()

    # Parse response
    content = json.loads(content)
    if content["status"] == "success":
        logger.debug("Authentication successful")
        attributes = content["attributes"]
        external_id = "surfconext/" + attributes["saml:sp:NameID"]["Value"]
        return HttpResponse(external_id)
    return HttpResponseBadRequest()


def ivoauth_callback(request):
    # Retrieve ticket given by ivoauth and use it
    ticket = request.GET.get("ticket", "")
    if not ticket:
        logger.error("no ticket")
    url = IVOAUTH_URL + "/status"
    post_data = [("token", IVOAUTH_TOKEN), ("ticket", ticket)]
    try:
        content = (
            urlopen(url, urlencode(post_data).encode("utf-8")).read().decode("utf-8")
        )
    except HTTPError:
        logger.error("Invalid url")
        return HttpResponseBadRequest()

    # Parse response
    content = json.loads(content)
    if content["status"] == "success":
        logger.debug("Authentication successful")
        attributes = content["attributes"]
        external_id = "surfconext/" + attributes["saml:sp:NameID"]["Value"]
        email = attributes["urn:mace:dir:attribute-def:mail"][0]
        person_set = Person.objects.filter(external_id=external_id)
        # If a person with external_id nonexistent, create new person
        if not person_set.exists():
            person = Person()
            person.handle = attributes["urn:mace:dir:attribute-def:uid"][0]
            try:
                surname = attributes["urn:mace:dir:attribute-def:sn"][0]
                first_name = attributes["urn:mace:dir:attribute-def:givenName"][0]
            except KeyError:
                person.name = person.handle
                first_name = ""
                surname = person.handle
                subject = "Surfconext login: missing 'givenName'"
                text_content = "handle: %s\n\n%s" % (person.handle, json.dumps(content))
                from_email = "warning@" + HOSTNAME
                to = ADMIN_NOTIFICATION_EMAIL
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.send(fail_silently=True)
            else:
                person.name = first_name + " " + surname
            # displayname = attributes["urn:mace:dir:attribute-def:displayName"][0]
            person.email = email
            person.public_email = False
            person.external_id = external_id
            person.save()

            ## Get communities for this person from ivoauth
            # TODO make this a generic method (so other auths can call it)
            # By default, add 'public' community
            person.communities.add(Community.objects.get(pk=1))
            # Get the rest from LDAP
            ldap_obj = ldap.initialize("ldap://ldap1.uva.nl:389")
            search_results = ldap_obj.search_s(
                "ou=Medewerkers,o=Universiteit van Amsterdam,c=NL",
                ldap.SCOPE_ONELEVEL,
                "(&(objectClass=person)(uid=" + person.handle + "))",
            )

            # Expect single search result
            if search_results:
                query, result = search_results[0]
                try:
                    supercommunity = Community.objects.get(name=result["o"][0])
                except Community.DoesNotExist:
                    pass
                else:
                    for community_name in result["ou"]:
                        subcommunity = supercommunity.subcommunities.filter(
                            name=community_name
                        )
                        if subcommunity.exists():
                            person.communities.add(subcommunity.get())
                            logger.debug("Community '" + community_name + "' added.")
                        else:
                            logger.debug("'" + community_name + "' not found.")
            else:
                logger.error("User has handle but LDAP can't find him/her!")
            logger.debug("Created new person '" + person.handle + "'")
            person.save()
        else:
            person = person_set.get()

        # Create new user if not already available
        if not person.user:
            try:
                user = User.objects.get(username=person.handle)
            except:
                user = User()
                user.username = person.handle
                user.first_name = person.name.split()[0]
                user.is_staff = True
                user.email = email
                user.set_password(utils.id_generator(size=12))
                user.save()
            person.user = user
            person.save()
            logger.debug("User '{}' linked to person '{}'".format(user, person))
        user = person.user
        user = authenticate(username=user.username)
        login(request, user)
        logger.debug("Logged in user '{}'".format(user))
    else:
        logger.debug("Authentication failed")
    return HttpResponseRedirect("/")


def cast_vote(request):
    # TODO explicitly define upvotes and downvotes
    # TODO something about not upvoting your own comments
    if request.method == "POST" and request.is_ajax():
        model_type = request.POST.get("model", None)
        model_id = request.POST.get("id", None)
        vote = request.POST.get("vote", None)
        if model_type is None or model_id is None or vote is None:
            return HttpResponseBadRequest()

        if request.user.is_authenticated:
            model = get_model_by_sub_id(model_type, int(model_id))
            user = Person.objects.get(user=request.user)
            if int(vote) == 1:
                if not model.upvoters.filter(pk=user.pk).exists():
                    if model.downvoters.filter(pk=user.pk).exists():
                        model.downvoters.remove(user)
                    else:
                        model.upvoters.add(user)
                else:
                    return HttpResponse("You can only vote once.", status=403)
            else:
                if not model.downvoters.filter(pk=user.pk).exists():
                    if model.upvoters.filter(pk=user.pk).exists():
                        model.upvoters.remove(user)
                    else:
                        model.downvoters.add(user)
                else:
                    return HttpResponse("You can only vote once.", status=403)
            model.save()
            return HttpResponse()
        else:
            return HttpResponse("You need to login first.", status=401)
    else:
        return HttpResponseBadRequest()


def loadquestionform(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return HttpResponse("You need to login first.", status=401)
        item_type = request.GET.get("model", "")
        item_id = int(request.GET.get("id", 0))

        logger.debug("initial questionform")
        questionform = QuestionForm(
            initial={"item_type": item_type, "item_id": item_id}
        )
        return render(
            request,
            "askquestion.html",
            {"form": questionform, "syntax": SEARCH_SETTINGS["syntax"]},
        )
    return HttpResponseBadRequest()


def submitquestion(request):
    if request.method == "POST":
        if request.is_ajax():
            try:
                request.POST._mutable = True
                request.POST["authors"] = request.user.person
                request.POST._mutable = False
            except Person.DoesNotExist:
                # TODO Present message to the user explaining that somehow
                # he is not linked to a person object.
                return HttpResponseNotFound()
            finally:
                request.POST._mutable = False
            questionform = QuestionForm(request.POST)
            logger.debug("request is POST")
            if questionform.is_valid():
                logger.debug("questionform valid")
                item_type = questionform.cleaned_data["item_type"]
                item_id = questionform.cleaned_data["item_id"]
                item = get_model_by_sub_id(item_type, item_id)
                question = questionform.save(commit=False)
                try:
                    question.authors = request.user.person
                except Person.DoesNotExist:
                    # TODO Present message to the user explaining that somehow
                    # he is not linked to a person object.
                    return HttpResponseNotFound()

                logger.debug("Question submitted by user '{}'".format(request.user))
                question.save()
                questionform.save_m2m()

                # Create reflexive links
                if item:
                    item.link(question)
                    question.link(item)

                # Assign communities
                c1 = set(item.communities.all())
                c2 = set(
                    flatten(
                        [author.communities.all() for author in question.authors.all()]
                    )
                )
                for community in c1.intersection(c2):
                    question.communities.add(community)

                data = json.dumps(
                    {"success": True, "redirect": question.get_absolute_url()}
                )

                # Send emails
                # To admin
                text_content = question.text
                html_content = (
                    "<h3><a href='http://"
                    + HOSTNAME
                    + question.get_absolute_url()
                    + "'>"
                    + question.title
                    + "</a></h3><p><i>by "
                    + ", ".join([a.name for a in question.authors.all()])
                    + "</i></p>"
                    + question.text
                )
                subject = "Starfish question: " + question.title
                from_email = "notifications@" + HOSTNAME
                to = ADMIN_NOTIFICATION_EMAIL
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=True)
                # To item author
                if item:
                    text_content = str(QUESTION_ASKED_TEXT).format(
                        author=", ".join([a.name for a in question.authors.all()]),
                        title=question.title,
                        questionlink=HOSTNAME + question.get_absolute_url(),
                        itemlink=HOSTNAME + item.get_absolute_url(),
                    )
                    html_content = (
                        "<h3><a href='http://"
                        + HOSTNAME
                        + question.get_absolute_url()
                        + "'>"
                        + question.title
                        + "</a></h3><p><i>by "
                        + ", ".join([a.name for a in question.authors.all()])
                        + "</i></p>"
                        + question.text
                    )
                    subject = "A question was asked"
                    from_email = "notifications@" + HOSTNAME
                    msg.attach_alternative(html_content, "text/html")
                    if isinstance(item, Person):
                        to_email = (item.email,)
                        msg = EmailMultiAlternatives(
                            subject, text_content, from_email, to_email
                        )
                        msg.send(fail_silently=True)
                    else:
                        for author in item.authors.all():
                            to_email = (author.email,)
                            msg = EmailMultiAlternatives(
                                subject, text_content, from_email, to_email
                            )
                            msg.send(fail_silently=True)
            else:
                logger.debug("questionform invalid")
                r = {
                    "success": False,
                    "errors": dict(
                        [
                            (k, [str(e) for e in v])
                            for k, v in questionform.errors.items()
                        ]
                    ),
                }
                data = json.dumps(r)
            return HttpResponse(data, content_type="application/json")
    return HttpResponseBadRequest()


def comment(request):
    if not request.user.is_authenticated:
        return HttpResponse("You need to login first.", status=401)
    if request.method == "POST":
        # This is a hack!
        request.POST._mutable = True
        request.POST["author"] = request.user.person
        request.POST["title"] = "comment"  # This is a placeholder
        request.POST._mutable = False
        commentform = CommentForm(request.POST)
        if commentform.is_valid():
            item_type = commentform.cleaned_data["item_type"]
            item_id = commentform.cleaned_data["item_id"]
            item = get_model_by_sub_id(item_type, item_id)
            if not item:
                logger.error(
                    "No item found for given type {} and id {}".format(
                        item_type, item_id
                    )
                )

            comment = commentform.save(commit=False)
            comment.author = request.user.person
            comment.save()
            commentform.save_m2m()

            # Send mail to comment author
            text_content = str(COMMENT_PLACED_TEXT).format(
                author=comment.author.name, itemlink=HOSTNAME + item.get_absolute_url()
            )
            html_content = (
                "<h3><a href='http://"
                + HOSTNAME
                + item.get_absolute_url()
                + "'>"
                + comment.author.name
                + "</i></p>"
                + comment.text
            )
            subject = "A comment was placed"
            from_email = "notifications@" + HOSTNAME
            to_email = (item.author.email,)
            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=True)

            logger.debug(
                "Comment by user '{}' on item {}/{}".format(
                    request.user, item_type, item_id
                )
            )
            item.comments.add(comment)
            if item_type == "Q":
                item.tags.add(*comment.tags.all())
            item.save()
            return HttpResponse("Comment added")
        else:
            return HttpResponseBadRequest("Input was not valid")
    else:
        return HttpResponseBadRequest("This HTTP method is not supported.")


def autocomplete(request):
    string = request.GET.get("q", "")
    if len(string) <= 0:
        return HttpResponse("[]", content_type="application/json")

    syntax = SEARCH_SETTINGS["syntax"]
    if string[0] == syntax["TAG"]:
        tags = Tag.objects.filter(handle__istartswith=string[1:])
        persons = []
        literals = []
    elif string[0] == syntax["PERSON"]:
        tags = []
        persons = Person.objects.filter(name__istartswith=string[1:])
        literals = []
    elif string[0] == syntax["LITERAL"]:
        tags = []
        persons = []
        literals = [string[1:]]
    else:
        tags = Tag.objects.filter(handle__istartswith=string)
        persons = Person.objects.filter(name__istartswith=string)
        # Suggestions based on titles
        # We have to query by type because TextItem is abstract
        objs = list(GoodPractice.objects.filter(title__istartswith=string))
        objs += list(Question.objects.filter(title__istartswith=string))
        objs += list(Information.objects.filter(title__istartswith=string))
        objs += list(Project.objects.filter(title__istartswith=string))
        objs += list(Event.objects.filter(title__istartswith=string))
        titles = [i.title for i in objs]
        literals = titles + [string]

    matches = []
    for tag in tags:
        matches.append(syntax["TAG"] + tag.handle)
    for person in persons:
        matches.append(syntax["PERSON"] + person.handle)
    for literal in literals:
        matches.append(syntax["LITERAL"] + literal + syntax["LITERAL"])
    return HttpResponse(json.dumps(matches), content_type="application/json")


def tag(request, handle):
    symb = quote(SEARCH_SETTINGS["syntax"]["TAG"])
    try:
        tag = Tag.objects.get(handle__iexact=handle)
    except:
        return redirect("/?q=" + symb + handle)
    if tag.glossary is not None:
        return redirect(tag.glossary.get_absolute_url())
    elif tag.alias_of is not None and tag.alias_of.glossary is not None:
        return redirect(tag.alias_of.glossary.get_absolute_url())
    else:
        return redirect("/?q=" + symb + handle)

def analytics(request):
    usercases = UserCase.objects.exclude(draft=True)
    questions = CPDQuestion.objects.all()
    scales = CPDScale.objects.all()

    q_counts = []
    for question in questions:
        l = UserCase.objects.filter(cpd_questions__question=question.question)
        q_counts.append((str(question), l.count(), [e.title for e in l], f"{question.scale.scale_type}-{question.question_nr}"))
        # logger.debug(f"{question.scale.scale_type}-{question.question_nr}")

    s_counts = []
    for scale in scales:
        l = UserCase.objects.filter(cpd_questions__scale__title=scale.title, cpd_questions__scale__scale_type=scale.scale_type, draft=False).distinct()
        s_counts.append((str(scale), l.count(), [e.title for e in l], scale.label))

    return render(
        request,
        "analytics.html",
        {
            "q_counts": q_counts,
            "s_counts": s_counts
        }
    )

# @cache_page(60 * 5)
def browse(request):
    user_communities = utils.get_user_communities(request.user)
    selected_community = request.GET.get("community", None)
    sort = request.GET.get("sort", "recent")
    if selected_community is not None:
        try:
            selected_community = Community.objects.get(pk=int(selected_community))
        except Community.DoesNotExist:
            selected_communities = user_communities
        else:
            selected_communities = [selected_community]
        # Filter check disabled, to allow anyone with access to link to view
        # selected_communities = filter(lambda x: x.id == selected_community,
        #        user_communities)
        selected_communities = utils.expand_communities(selected_communities)
    else:
        selected_communities = user_communities

    recent = sort == "recent"

    good_practices = GoodPractice.objects.filter(communities__in=selected_communities, draft=False).distinct().order_by("featured", "create_date" if recent else "title" )
    projects = Project.objects.filter(communities__in=selected_communities, draft=False).distinct().order_by("featured", "create_date" if recent else "title" )
    events = Event.objects.filter(communities__in=selected_communities, draft=False).distinct().order_by("featured", "create_date" if recent else "title" )
    glossaries = Glossary.objects.filter(communities__in=selected_communities, draft=False).distinct().order_by("featured", "create_date" if recent else "title" )
    informations = Information.objects.filter(communities__in=selected_communities, draft=False).distinct().order_by("featured", "create_date" if recent else "title" )
    questions = Question.objects.filter(communities__in=selected_communities, draft=False).distinct().order_by("featured", "create_date" if recent else "title" )
    user_cases = UserCase.objects.filter(communities__in=selected_communities, draft=False).distinct().order_by("featured", "create_date" if recent else "title" )

    people = Person.objects.filter(communities__in=selected_communities, draft=False, is_ghost=False).distinct().order_by("featured", "create_date" if recent else "name" )

    cpd_scenarios = []

    for case in user_cases:
        cpd_scenario = case.get_cpd_scenario()
        case.cpd_scenario = cpd_scenario
        if cpd_scenario:
            cpd_scenarios.append(cpd_scenario)

    results = {
        "GoodPractice": good_practices,
        "Project": projects,
        "Event": events,
        "Glossary": glossaries,
        "Information": informations,
        "Person": people,
        "Question": questions,
        "UserCase": user_cases,
        "CPDScenario": cpd_scenarios
    }

    # Find first type that has nonzero value count
    first_active = ""
    for key in results:
        if len(results[key]):
            first_active = key.lower()
            break

    return render(
        request,
        "browse.html",
        {
            "user_communities": user_communities,
            "results": results,
            "cols": 1,
            "sort": sort,
            "first_active": first_active,
        },
    )

@check_profile_completed
def search(request):
    user_communities = utils.get_user_communities(request.user)
    string = request.GET.get("q", "")
    sort = request.GET.get("sort", "recent")
    community = request.GET.get("community", "")
    if len(string) > 0:
        # Check if community selected, if so, use it
        if community.isdigit() and int(community) > 0:
            community = int(community)
            try:
                search_communities = [Community.objects.get(pk=int(community))]
            except Community.DoesNotExist:
                search_communities = user_communities
        else:
            search_communities = user_communities
        query, dym_query, dym_query_raw, results, special = retrieval.retrieve(
            string, True, search_communities
        )

        def sorting_key(item):
            if sort == "recent":
                date_ref = datetime.now(timezone.utc)
                return (item["featured"], date_ref - item["create_date"])
            else:
                if item["type"] == "Person":
                    return (item["featured"], item["name"].split(" ")[-1])
                else:
                    return (item["featured"], item["title"])

        results_by_type = dict()
        for result in results:
            try:
                results_by_type["".join(result["type"].split())].append(result)
            except KeyError:
                results_by_type["".join(result["type"].split())] = [result]

        for l in results_by_type.values():
            l.sort(key=sorting_key)

        tag_tokens, person_tokens, literal_tokens = utils.parse_query(query)

        # Extract the tokens, discard location information
        tag_tokens = map(lambda x: x[0], tag_tokens)
        person_tokens = map(lambda x: x[0], person_tokens)
        literal_tokens = map(lambda x: x[0], literal_tokens)

        tag_tokens = retrieval.get_synonyms(tag_tokens)
        q_tags = Tag.objects.filter(handle__in=tag_tokens)

        q_types = set()
        for tag in q_tags:
            q_types.add(tag.type)

        # Find first type that has nonzero value count
        for type_id, type_name in ITEM_TYPES:
            if type_name.replace(" ", "") in results_by_type:
                first_active = type_name.replace(" ", "").lower()
                break
        else:
            first_active = ""

        # Sort tags by type and alphabetically
        for l in results_by_type.values():
            for result in l:
                t_sorted = sorted_tags(result["tags"]).values()
                # Don't show 'irrelevant' tags
                filtered = []
                for by_type in t_sorted:
                    filtered.append(
                        filter(
                            lambda x: (
                                x["type"] not in q_types or x["handle"] in tag_tokens
                            ),
                            by_type,
                        )
                    )
                trimmed = []
                for t in filtered:
                    t = list(t)
                    if len(t) > 1:
                        # TODO: pick one
                        handle = str("+" + str(len(t) - 1) + " " + t[0]["type_name"])
                        dom_id = str(result["id"]) + t[0]["type"]
                        trimmed.append(
                            [t[0], {"handle": handle, "more": t[1:], "dom_id": dom_id}]
                        )
                    else:
                        trimmed.append(t)
                # FIXME fix collapsed tags in browse/search page
                # and fix CPD tags being filtered out by the logic above
                # result["tags"] = itertools.chain(*trimmed)
        used_tags_by_type = []
    else:
        query = ""
        dym_query = query
        dym_query_raw = query
        results_by_type = {}
        special = None
        first_active = ""

        used_tags = set(
            Tag.objects.raw(
                """
        SELECT t.id, t.handle, t.type
        FROM search_tag as t
        WHERE EXISTS (
            SELECT sic.id, sic.item_id, sic.community_id
            FROM search_item_communities as sic
            WHERE sic.community_id IN ("""
                + ",".join([str(uc.id) for uc in user_communities])
                + """)
                AND EXISTS (
                    SELECT sit.id, sit.item_id, sit.tag_id
                    FROM search_item_tags as sit
                    WHERE sit.item_id = sic.item_id
                        AND t.id = sit.tag_id
            )
        )
        """
            )
        )

        used_tags_by_type = []
        for tag_type in Tag.TAG_TYPES:
            tags = [tag.handle for tag in used_tags if tag.type == tag_type[0]]
            random.shuffle(tags)
            used_tags_by_type.append([tag_type, sorted(tags[0:3])])

    # do not return events that are past due date
    # if 'Event' in results_by_type:
    #    results_by_type['Event'] = [e for e in results_by_type['Event']
    #                                if not e['is_past_due']]

    new_users = 0

    if request.user.is_staff:
        new_users = len(Person.objects.filter(draft=True))

    pending_invitations = []

    if request.user.is_authenticated:
        if Person.objects.filter(user=request.user).exists():
            pending_invitations = ItemAuthor.objects.filter(
                status="PENDING", person=Person.objects.get(user=request.user)
            )

    return render(
        request,
        "index.html",
        {
            "special": special,
            "results": results_by_type,
            "syntax": SEARCH_SETTINGS["syntax"],
            "query": query,
            "dym_query": dym_query,
            "dym_query_raw": dym_query_raw,
            "cols": 1,  # replaces len(results_by_type)
            "first_active": first_active,
            "user_communities": user_communities,
            "community": community,
            "sort": sort,
            "new_users": new_users,
            "used_tags": used_tags_by_type,
            "has_pending_invitations": len(pending_invitations) > 0,
            "pending_invitations": pending_invitations,
        },
    )


@user_passes_test(lambda u: u.is_superuser)
def validate_profiles(request):
    profiles = Person.objects.filter(draft=True)
    return render(request, "validate_profiles.html", {"profiles": profiles})


def privacy_policy(request):
    return render(request, "privacy-policy.html")


def terms_of_service(request):
    return render(request, "terms-of-service.html")


@user_passes_test(lambda u: u.is_superuser)
def validate_accept(request):
    _id = request.GET.get("person", -1)

    if int(_id) > 0:
        p = Person.objects.get(id=_id)
        p.draft = False
        p.save()

    return redirect("/validate")


@user_passes_test(lambda u: u.is_superuser)
def validate_reject(request):
    _id = request.GET.get("person", -1)

    if int(_id) > 0:
        p = Person.objects.get(id=_id)
        p.delete()

    return redirect("/validate")


@login_required
def accept_invitation(request):
    ia = get_object_or_404(ItemAuthor, pk=request.GET.get("pk", -1))
    ia.status = "ACCEPTED"
    ia.save()

    return redirect("/")


@login_required
def decline_invitation(request):
    ia = get_object_or_404(ItemAuthor, pk=request.GET.get("pk", -1))
    ia.status = "DECLINED"
    ia.save()

    return redirect("/")


def feedback(request):
    user_communities = utils.get_user_communities(request.user)
    return render(request, "feedback.html", {"user_communities": user_communities})


def search_list(request):
    user_communities = utils.get_user_communities(request.user)
    string = request.GET.get("q", "")
    if len(string) > 0:
        query, dym_query, dym_query_raw, results, special = retrieval.retrieve(
            string, True, user_communities
        )

        def compare(item1, item2):
            """
            Sort based on scope, featured, mentioned in query, score, date.
            """
            if item1["score"] != item2["score"]:
                return int(round(item1["score"] - item2["score"]))
            if item1["featured"] ^ item2["featured"]:
                return int(round(item1["featured"] - item2["featured"]))
            return int(
                round(item1["create_date"] < item2["create_date"])
                - (item1["create_date"] > item2["create_date"])
            )

            # TODO scope
            # TODO mentioned in query
            # TODO separate persons?

        results.sort(compare)

        tag_tokens, person_tokens, literal_tokens = utils.parse_query(query)

        # Extract the tokens, discard location information
        tag_tokens = map(lambda x: x[0], tag_tokens)
        person_tokens = map(lambda x: x[0], person_tokens)
        literal_tokens = map(lambda x: x[0], literal_tokens)

        tag_tokens = retrieval.get_synonyms(tag_tokens)
        q_tags = Tag.objects.filter(handle__in=tag_tokens)

        q_types = set()
        for tag in q_tags:
            q_types.add(tag.type)

        # Sort tags by type and alphabetically
        for result in results:
            t_sorted = sorted_tags(result["tags"]).values()
            # Don't show 'irrelevant' tags
            filtered = []
            for by_type in t_sorted:
                filtered.append(
                    filter(
                        lambda x: (
                            x["type"] not in q_types or x["handle"] in tag_tokens
                        ),
                        by_type,
                    )
                )
            trimmed = []
            for t in filtered:
                if len(t) > 1:
                    # TODO: pick one
                    handle = "+" + str(len(t) - 1) + " " + t[0]["type_name"]
                    dom_id = str(result["id"]) + t[0]["type"]
                    trimmed.append(
                        [t[0], {"handle": handle, "more": t[1:], "dom_id": dom_id}]
                    )
                else:
                    trimmed.append(t)
            result["tags"] = itertools.chain(*trimmed)

    else:
        query = ""
        dym_query = query
        dym_query_raw = query
        results = []
        special = None

    return render(
        request,
        "index_list.html",
        {
            "special": special,
            "results": results,
            "syntax": SEARCH_SETTINGS["syntax"],
            "query": query,
            "dym_query": dym_query,
            "dym_query_raw": dym_query_raw,
            "user_communities": user_communities,
        },
    )


def get_model_by_sub_id(model_type, model_id):
    """We know the model_id and type, but the id
    identifies it among its equals.. and not all models!
    """
    # TODO replace using downcast
    model = None
    if model_type == "P":
        model = Person.objects.get(pk=model_id)
    elif model_type == "G":
        model = GoodPractice.objects.get(pk=model_id)
    elif model_type == "I":
        model = Information.objects.get(pk=model_id)
    elif model_type == "R":
        model = Project.objects.get(pk=model_id)
    elif model_type == "E":
        model = Event.objects.get(pk=model_id)
    elif model_type == "Q":
        model = Question.objects.get(pk=model_id)
    elif model_type == "C":
        model = Comment.objects.get(pk=model_id)
    elif model_type == "S":
        model = Glossary.objects.get(pk=model_id)
    return model
