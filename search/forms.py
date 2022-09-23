from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from django.forms import (
    CharField,
    EmailInput,
    HiddenInput,
    IntegerField,
    ModelForm,
    ModelMultipleChoiceField,
    PasswordInput,
    SelectMultiple,
    Textarea,
)

from search.models import (
    Comment,
    Community,
    CPDLearningEnvironment,
    CPDQuestion,
    Link,
    Event,
    Glossary,
    GoodPractice,
    Information,
    Item,
    Person,
    Project,
    Question,
    UserCase,
)
from search.widgets import TagInput

# from bootstrap3_datetime.widgets import DateTimePicker


class LoginForm(ModelForm):
    password = CharField(widget=PasswordInput)
    email = CharField(widget=EmailInput)

    class Meta:
        model = Person
        fields = ["email", "password"]


class RegisterForm(ModelForm):
    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    handle = CharField(max_length=100)
    password = CharField(widget=PasswordInput)
    email = CharField(widget=EmailInput)
    university = CharField(max_length=500)
    introduction = CharField(widget=Textarea)

    class Meta:
        model = get_user_model()
        fields = ["password", "handle", "first_name", "last_name", "email"]


class CommentForm(ModelForm):
    item_type = CharField(widget=HiddenInput())
    item_id = IntegerField(widget=HiddenInput())

    class Meta:
        model = Comment
        fields = ["text", "tags"]

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields["tags"].widget = TagInput()
        self.fields["tags"].help_text = None


class QuestionForm(ModelForm):
    item_type = CharField(widget=HiddenInput())
    item_id = IntegerField(widget=HiddenInput())

    class Meta:
        model = Question
        fields = ["title", "text", "tags"]

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields["tags"].widget = TagInput()
        self.fields["tags"].help_text = None


class DashboardForm(ModelForm):
    def __init__(self, *args, **kwargs):
        if "communities" in kwargs:
            communities = kwargs["communities"]
            del kwargs["communities"]
        else:
            communities = Community.objects
        super(DashboardForm, self).__init__(*args, **kwargs)
        self.fields["tags"].widget = TagInput()
        self.fields["tags"].help_text = None
        if "links" in self.fields:
            self.fields["links"] = ModelMultipleChoiceField(
                Item.objects.order_by("type"), widget=SelectMultiple, required=False
            )

        if "communities" in self.fields:
            self.fields["communities"] = ModelMultipleChoiceField(
                communities, widget=SelectMultiple
            )
        """
        if 'date' in self.fields:
             self.fields['date'].widget = \
                 DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                         "pickSeconds": False})
        """

    class Media:
        js = ["/admin/jsi18n/"]
        css = {
            "all": ["admin/css/widgets.css", "css/m2m_form_widget.css"],
        }


class EditInformationForm(DashboardForm):
    class Meta:
        model = Information
        fields = ["title", "text", "links", "authors", "communities", "tags", "draft"]


class EditCommentForm(DashboardForm):
    class Meta:
        model = Information
        fields = ["title", "text", "tags"]


class EditGoodPracticeForm(DashboardForm):
    class Meta:
        model = GoodPractice
        fields = ["title", "text", "links", "authors", "communities", "tags", "draft"]


class EditQuestionForm(DashboardForm):
    class Meta:
        model = Question
        fields = ["title", "text", "links", "authors", "communities", "tags"]


class EditUserCaseForm(DashboardForm):
    cpd_questions = ModelMultipleChoiceField(
        queryset=CPDQuestion.objects.all(),
        widget=FilteredSelectMultiple(CPDQuestion._meta.verbose_name_plural, False),
        required=False,
    )

    links = ModelMultipleChoiceField(
        queryset=Link.objects.all(),
        widget=FilteredSelectMultiple(Link._meta.verbose_name_plural, False),
        required=False,
    )

    communities = ModelMultipleChoiceField(
        queryset=Community.objects.all(),
        widget=FilteredSelectMultiple(Community._meta.verbose_name_plural, False),
        required=False,
    )

    cpd_learning_environment = ModelMultipleChoiceField(
        queryset=CPDLearningEnvironment.objects.all(),
        widget=SelectMultiple,
        required=False,
    )

    class Meta:
        model = UserCase
        fields = [
            "title",
            "text",
            "draft",
            "wallpaper",
            "tags",
            "context_goals",
            "cpd_activities",
            "evaluation",
            "links",
            "communities",
            "authors",
            "cpd_questions",
            "cpd_time_to_finish",
            "cpd_learning_environment",
        ]


class EditPersonForm(DashboardForm):
    class Meta:
        model = Person
        fields = [
            "title",
            "name",
            "headline",
            "about",
            "photo",
            "website",
            "public_email",
            "email",
            "communities",
        ]


class EditProjectForm(DashboardForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "text",
            "contact",
            "authors",
            "communities",
            "links",
            "tags",
            "draft",
        ]


class EditEventForm(DashboardForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "text",
            "contact",
            "authors",
            "communities",
            "links",
            "tags",
            "date",
            "draft",
        ]


class EditGlossaryForm(DashboardForm):
    class Meta:
        model = Glossary
        fields = ["title", "text", "tags", "authors", "links", "communities", "draft"]
