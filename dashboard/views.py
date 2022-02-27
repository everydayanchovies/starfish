from django.contrib import messages
from django.db.models import Q
from django.forms.models import modelform_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.context_processors import csrf
from django.views import generic

from dashboard.forms import *
from search.forms import *
from search.models import *
from search.utils import parse_tags, get_user_communities

SEARCH_SETTINGS = settings.SEARCH_SETTINGS
TAG_REQUEST_MESSAGE = settings.TAG_REQUEST_MESSAGE
ACCOUNT_UPDATED_MSG = settings.ACCOUNT_UPDATED_MSG
ITEM_UPDATED_MSG = settings.ITEM_UPDATED_MSG


class QuerySetMock:
    def __init__(self, l, qs):
        self.l = l
        self.qs = qs

    def __getattribute__(self, key):
        if key == "all" or key == "l":
            return super(QuerySetMock, self).__getattribute__(key)
        else:
            qs = super(QuerySetMock, self).__getattribute__('qs')
            return qs.__getattribute__(key)

    def all(self):
        return self.l


def contribute(request):
    return render(request, 'contribute_options.html',
                  {'user_communities': get_user_communities(request.user)})


def contributions(request):
    if request.user.is_authenticated:
        person = Person.objects.get(user=request.user)
        c = {}

        colab = ItemAuthor.objects.filter(person=person, status='ACCEPTED').values_list('item', flat=True)
        c['goodpractice'] = GoodPractice.objects.filter(Q(author=person) | Q(id__in=colab)).order_by(
            'title')  # | ItemAuthor.objects.filter(person=person.email).values('item')
        c['information'] = Information.objects.filter(Q(author=person) | Q(id__in=colab)).order_by('title')
        c['project'] = Project.objects.filter(Q(author=person) | Q(id__in=colab)).order_by('title')
        c['event'] = Event.objects.filter(Q(author=person) | Q(id__in=colab)).order_by('title')
        c['question'] = Question.objects.filter(Q(author=person) | Q(id__in=colab)).order_by('title')
        c['glossary'] = Glossary.objects.filter(Q(author=person) | Q(id__in=colab)).order_by('title')
        c['usercase'] = UserCase.objects.filter(Q(author=person) | Q(id__in=colab)).order_by('title')
        return render(request, 'contributions.html', {
            'user_communities': get_user_communities(request.user),
            'c': c})
    else:
        # TODO usability
        return HttpResponse("Please log in.")


def edit_me(request):
    if request.user.is_authenticated:
        person = Person.objects.get(user=request.user)
        PersonForm = modelform_factory(Person,
                                       fields=('headline', 'email', 'website', 'public_email', 'about', 'photo'))
        if request.method == "POST":
            if request.FILES.get('photo'):
                person.photo = request.FILES.get('photo')
                person.save()

            form = PersonForm(request.POST, instance=person)
            if form.is_valid():
                form.save()

            messages.add_message(request, messages.INFO,
                                 ACCOUNT_UPDATED_MSG.format('profile'))
            return render(request, 'dashboard_person.html', {
                'user_communities': get_user_communities(request.user),
                'form': form,
                'person': person,
                'syntax': SEARCH_SETTINGS['syntax']})
        else:
            return render(request, 'dashboard_person.html', {
                'user_communities': get_user_communities(request.user),
                'form': PersonForm(instance=person),
                'person': person,
                'syntax': SEARCH_SETTINGS['syntax']})
    else:
        # TODO usability
        return HttpResponse("Please log in.")


def account_settings(request):
    if request.user.is_authenticated:
        person = Person.objects.get(user=request.user)
        emailform = ChangeEmailForm(request.POST)
        passwordform = ChangePasswordForm(request.POST)

        if request.method == "POST":
            if emailform.is_valid():
                email = emailform.cleaned_data['newemail']
                if email:
                    person.email = email
                    messages.add_message(request, messages.INFO,
                                         ACCOUNT_UPDATED_MSG.
                                         format('email adddress'))
            if passwordform.is_valid():
                newpwd = passwordform.cleaned_data['newpassword']
                if newpwd:
                    u = request.user
                    u.set_password(newpwd)
                    u.save()
                    messages.add_message(request, messages.INFO,
                                         ACCOUNT_UPDATED_MSG.format('password'))
            return render(request, 'account_settings.html', {
                'emailform': emailform,
                'passwordform': passwordform,
                'person': person,
                'syntax': SEARCH_SETTINGS['syntax']})
        else:
            return render(request, 'account_settings.html', {
                'emailform': ChangeEmailForm(),
                'passwordform': ChangePasswordForm(),
                'person': person,
                'syntax': SEARCH_SETTINGS['syntax']})

    else:
        # TODO what now?
        return HttpResponse("Please log in.")


class EditForm(generic.View):
    success_url = "/dashboard/"

    def alter_form(self, form):
        '''
        if 'links' in form.fields:
            qs = form.fields['links'].queryset
            links = sorted(qs, key=(lambda x: (x.type,
                x.downcast().name.strip().split(" ")[-1]
                if x.type == "P" else x.downcast().title)))

            form.fields['links'].queryset = QuerySetMock(links, qs)
        
        if 'contact' in form.fields:
            qs = form.fields['contact'].queryset
            persons = sorted(qs, key=(lambda x:
                x.downcast().name.strip().split(" ")[-1]))

            form.fields['contact'].queryset = QuerySetMock(persons, qs)
        '''
        return form

    def get(self, request, *args, **kwargs):
        """Get a form for a new or existing Object."""

        if request.user.is_authenticated:

            if request.user.person.draft:
                return render(request, 'no_access.html')

            # Communities
            user_communities = get_user_communities(request.user)
            communities = Community.objects.filter(pk__in=[c.id for c in
                                                           user_communities])

            # Existing object
            elems = request.path.strip("/").split("/")
            try:
                obj_id = int(elems[2])
                obj = get_object_or_404(self.model_class, pk=obj_id)
                form = self.form_class(instance=obj, communities=communities)
                form = self.alter_form(form)
                c = {
                    "obj": obj,
                    "authors": obj.authors,
                    "links": Item.objects.order_by('type'),
                    "all_communities": Community.objects.all(),
                    "form_communities": communities,
                    "user_communities": user_communities,
                    "form": form
                }

                if self.model_class == UserCase:
                    c["wallpaper_url"] = obj.wallpaper
            except ValueError:
                if self.model_class == UserCase:
                    form = self.form_class(
                        {
                            "text": get_template(self.model_class),
                            "context_goals": "<h2>Local context (specific)</h2><br /><h2>Local CPD goals</h2>",
                            "cpd_activities": "<h2>CPD activities at the local university</h2><br /><h2>Teaching and learning materials</h2><br /><h2>Sustainable implementation</h2>",
                            "evaluation": "<h2>Expected impact of the CPD User Case</h2><br /><h2>Plans for eventual continuation of the CPD within the same topic</h2>"
                        },
                        communities=communities)
                else:
                    form = self.form_class(
                        {"text": get_template(self.model_class)},
                        communities=communities)

                form = self.alter_form(form)
                c = {
                    "links": Item.objects.order_by('type'),
                    "form": form,
                    "all_communities": Community.objects.all(),
                    "form_communities": communities,
                    "user_communities": user_communities,
                    "is_new": True
                }

            c.update(csrf(request))
            # renderer=form.renderer
            return render(request, self.template_name, c, )
        else:
            # TODO usability
            return HttpResponse("Please log in.")

    def post(self, request, *args, **kwargs):
        """Post a new object or update existing"""

        if request.user.is_authenticated:
            # Communities
            user_communities = get_user_communities(request.user)
            communities = Community.objects.filter(pk__in=[c.id for c in
                                                           user_communities])

            # Existing object
            elems = request.path.strip("/").split("/")
            post_v = request.POST.copy()
            post_v["author"] = request.user.person.id
            try:
                obj_id = int(elems[-1])
                obj = get_object_or_404(self.model_class, pk=obj_id)
                if obj.author:
                    post_v["author"] = obj.author.id
                form = self.form_class(post_v, instance=obj,
                                       communities=communities)
            except ValueError:  # New object
                form = self.form_class(post_v, communities=communities)
            if form.is_valid():
                # Check if all tags are already known
                tag_str = form.data.get('tags', None)
                if tag_str:
                    tags, unknown_tags = parse_tags(tag_str)
                    if unknown_tags['token'] or unknown_tags['person'] or \
                            unknown_tags['literal']:
                        messages.info(request, TAG_REQUEST_MESSAGE)
                if self.success_url[-1] == '/':
                    obj = form.save(commit=False)
                    obj.save()
                    obj_id = str(obj.pk)
                    links = form.cleaned_data.get('links')
                    for link in links:
                        obj.link(link)
                    del form.cleaned_data['links']
                    form.save_m2m()
                else:
                    obj = form.save(commit=False)
                    obj.save()
                    obj_id = '/' + str(obj.pk)
                    links = form.cleaned_data.get('links')
                    for link in links:
                        obj.link(link)
                    del form.cleaned_data['links']
                    form.save_m2m()
                redirect = self.success_url + obj_id

                messages.add_message(request, messages.INFO,
                                     ITEM_UPDATED_MSG.format(self.model_class.__name__))
                return HttpResponseRedirect(redirect)
            else:
                return render(request, self.template_name, {
                    'user_communities': user_communities,
                    'form': form})
        else:
            # TODO usability
            return HttpResponse("Please log in.")


class InformationForm(EditForm):
    template_name = "information_form.html"
    form_class = EditInformationForm
    model_class = Information
    success_url = "/dashboard/information"


class GoodPracticeForm(EditForm):
    template_name = "goodpractice_form.html"
    form_class = EditGoodPracticeForm
    model_class = GoodPractice
    success_url = "/dashboard/goodpractice"


class EventForm(EditForm):
    template_name = "event_form.html"
    form_class = EditEventForm
    model_class = Event
    success_url = "/dashboard/event"


class ProjectForm(EditForm):
    template_name = "project_form.html"
    form_class = EditProjectForm
    model_class = Project
    success_url = "/dashboard/project"


class QuestionForm(EditForm):
    template_name = "question_form.html"
    form_class = EditQuestionForm
    model_class = Question
    success_url = "/dashboard/question"


class UserCaseForm(EditForm):
    template_name = "user_case_form.html"
    form_class = EditUserCaseForm
    model_class = UserCase
    success_url = "/dashboard/usercase"

    def post(self, request, *args, **kwargs):
        if request.POST.get('title'):
            match = UserCase.objects.filter(title=request.POST.get('title'))
            if len(match) == 1 and request.FILES.get('wallpaper'):
                match[0].wallpaper = request.FILES.get('wallpaper')
                match[0].save()

        return super().post(request, args, kwargs)


class GlossaryForm(EditForm):
    template_name = "glossary_form.html"
    form_class = EditGlossaryForm
    model_class = Glossary
    success_url = "/dashboard/glossary"
