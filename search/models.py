import re
from datetime import datetime
from html.parser import HTMLParser

import ckeditor_uploader.fields as ck_field
import wikipedia
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone

ITEM_TYPES = settings.ITEM_TYPES


def get_template(item):
    if item == GoodPractice:
        item = "G"
    elif item == Project:
        item = "R"
    elif item == Information:
        item = "I"
    elif item == Event:
        item = "E"
    elif item == Person:
        item = "P"
    elif item == Glossary:
        item = "S"
    elif item == Question:
        item = "Q"
    elif item == UserCase:
        item = "U"
    try:
        return Template.objects.get(type=item).template
    except (Template.DoesNotExist, AttributeError):
        return ""



class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return " ".join(self.fed)


def strip_tags(html):
    if html is None:
        return ""

    s = MLStripper()
    s.feed(html)
    return s.get_data()


def cleanup_for_search(raw_text):
    """
    Cleanup raw_text to be suited for matching in search.
    Operations:
      - Strip HTML tags
      - Remove newlines, returns and tab characters
      - Trim double and trailing spaces
      - Convert to lower case
      - Remove URLs
      - Remove email addresses
    """
    # Strip HTML tags
    text = strip_tags(raw_text)
    # Remove newlines, returns and tab characters
    text = re.sub(r"[\t\n\r]", "", text)
    # Trim double and trailing spaces
    text = re.sub(r" +", " ", text).strip()
    # Convert to lower case
    text = text.lower()
    # Remove URLs
    text = re.sub(r"\b(https?|ftp)://[^\s/$.?#].[^\s]*\b", "", text)
    # Remove email addresses
    text = re.sub(r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}\b", "", text)
    return text


class CPDTimeToFinish(models.Model):
    title = models.CharField(max_length=255)
    inline_title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "CPD Time To Finish"
        verbose_name_plural = "CPD Time To Finish Entries"


class CPDLearningEnvironment(models.Model):
    title = models.CharField(max_length=255)
    inline_title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "CPD Learning Environment"
        verbose_name_plural = "CPD Learning Environment Entries"


## Pseudomodel, created to account for the way the search module works
## If the search module is rewritten, this class can be dropped
class CPDScenario:
    id = []
    scales = []
    time_to_finish = None
    learning_environments = []

    def from_usercase(usercase_id):
        usercase = UserCase.objects.get(pk=usercase_id)

        cpd_scenario = CPDScenario()
        cpd_scenario.scales = [q.scale for q in usercase.cpd_questions.all()]
        if not cpd_scenario.scales:
            return None

        cpd_scenario.time_to_finish = usercase.cpd_time_to_finish
        cpd_scenario.learning_environments = usercase.cpd_learning_environment.all()

        cpd_scenario.type = "CPDScenario"
        cpd_scenario.featured = datetime.now(timezone.utc)
        cpd_scenario.create_date = datetime.now(timezone.utc)

        w_scale_ids = [s.id for s in cpd_scenario.scales]
        w_scale_ids.sort()
        cpd_scenario.id = "".join([str(s_id) for s_id in w_scale_ids])
        return cpd_scenario

    def dict_format(self, obj=None):
        if obj is None:
            obj = {}
        obj = obj.copy()
        obj.update(
            {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "scales": [s.dict_format() for s in list(self.scales)],
                "tags": [s.tag.dict_format() for s in list(self.scales)],
            }
        )
        return obj

    @property
    def scales_competences(self):
        return [s for s in self.scales if s.scale_type == CPDScale.ST_COMPETENCES]

    @property
    def scales_attitudes(self):
        return [s for s in self.scales if s.scale_type == CPDScale.ST_ATTITUDES]

    @property
    def scales_activities(self):
        return [s for s in self.scales if s.scale_type == CPDScale.ST_ACTIVITIES]

    @property
    def classification_scales(self):
        if competencies := self.scales_competences:
            return competencies
        elif attitudes := self.scales_attitudes:
            return attitudes
        elif activities := self.scales_activities:
            return activities
        return []

    @property
    def title(self):
        scales = list(dict.fromkeys(self.classification_scales))
        return f"{', '.join([s.title for s in scales])} (type {', '.join([s.label for s in scales])})"

    @property
    def description(self):

        competences = self.scales_competences
        attitudes = self.scales_attitudes

        w_text = ""

        if competences:
            w_text += "This CPD scenario describes a User case in which lecturers develop their competence in "
            w_text += " and ".join([s.inline_title.lower() for s in sorted(set(competences), key=lambda x: x.label)])
            w_text += " "

            if attitudes:
                w_text += "and develop attitudes in "

        elif attitudes:
            w_text += "This CPD scenario describes a User case in which lecturers develop attitudes in "


        if attitudes:
            w_text += " and ".join([s.inline_title.lower() for s in sorted(set(attitudes), key=lambda x: x.label)])

        w_text = w_text.strip()
        w_text += ".\n"

        if time_to_finish := self.time_to_finish:
            w_text += (
                "The approximate duration of a User case that follows this scenario is "
            )
            w_text += time_to_finish.inline_title.lower()

            w_text = w_text.strip()
            w_text += ".\n"

        if learning_environments := self.learning_environments:
            w_text += "In this CPD scenario the participants "
            w_text += " and ".join(
                [le.inline_title.lower() for le in learning_environments]
            )

            w_text = w_text.strip()
            w_text += "."

        return w_text


class CPDScale(models.Model):
    ST_COMPETENCES = "P1"
    ST_ATTITUDES = "P2"
    ST_ACTIVITIES = "P3"
    SCALE_TYPE_CHOICES = [
        (ST_COMPETENCES, "Competences"),
        (ST_ATTITUDES, "Attitudes"),
        (ST_ACTIVITIES, "CPD Activities"),
    ]

    title = models.CharField(max_length=255)
    inline_title = models.CharField(max_length=255)
    scale_parent = models.ForeignKey(
        "CPDScale", on_delete=models.SET_NULL, null=True, blank=True
    )
    scale_type = models.CharField(
        max_length=50, choices=SCALE_TYPE_CHOICES, default=ST_COMPETENCES
    )
    scale = models.CharField(max_length=3)

    @property
    def label(self):
        if parent := self.scale_parent:
            return f"{parent.label}{self.scale}"
        else:
            return f"{self.scale_type}-{self.scale}"

    def __str__(self):
        return f"{self.label} - {self.title}"

    def save(self, *args, **kwargs):
        # if parent_scale is set, inherit its scale_type
        if parent := self.scale_parent:
            self.scale_type = parent.scale_type

        super(CPDScale, self).save(*args, **kwargs)

        # create related tag
        if not self.tag:
            tag = Tag(type=Tag.TT_CPD, handle=self.label)
            tag.save()

    @property
    def tag(self):
        if found_tags := Tag.objects.filter(type=Tag.TT_CPD, handle=self.label):
            return found_tags[0]
        return None

    def dict_format(self, obj=None):
        # Fill dict format at this level
        # make sure the pass by reference does not cause unexpected results
        if obj is None:
            obj = {}
        obj = obj.copy()
        obj.update(
            {
                "id": self.id,
                "title": self.title,
                "scale_parent": self.scale_parent.dict_format()
                if self.scale_parent
                else "",
                "scale_type": self.scale_type,
            }
        )
        return obj

    class Meta:
        verbose_name = "CPD Scale"
        verbose_name_plural = "CPD Scales"

        unique_together = (("scale_type", "scale", "scale_parent"),)


class CPDQuestion(models.Model):
    question = models.CharField(max_length=255)
    scale = models.ForeignKey("CPDScale", on_delete=models.CASCADE)
    question_nr = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.scale.scale_type}-{self.question_nr} {self.question}"

    class Meta:
        verbose_name = "CPD Question"
        verbose_name_plural = "CPD Questions"


class Tag(models.Model):
    TT_PEDAGOGY = "P"
    TT_TECHNOLOGY = "T"
    TT_CONTENT = "C"
    TT_CONTEXT = "O"
    TT_CPD = "D"
    TAG_TYPES = (
        (TT_PEDAGOGY, "Pedagogy"),
        (TT_TECHNOLOGY, "Technology"),
        (TT_CONTENT, "Content"),
        (TT_CONTEXT, "Context/Topic"),
        (TT_CPD, "Special/CPD"),
    )
    # The type of this tag, used for coloring
    type = models.CharField(max_length=1, choices=TAG_TYPES)
    # The handle by which this tag will be identified
    handle = models.CharField(max_length=255, unique=True)
    # The glossary item that explains the tag
    # TODO: use a one-to-one relationship instead of a foreign key
    glossary = models.ForeignKey(
        "Glossary", on_delete=models.SET_NULL, null=True, blank=True, unique=True
    )
    # The reference to the Tag of which this is an alias (if applicable)
    alias_of = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )

    info_link = models.CharField(max_length=300, null=True, blank=True)

    description = models.TextField(null=True, blank=True)

    def dict_format(self):
        """representation used to communicate the model to the client."""
        alias_of_handle = None
        if self.alias_of:
            alias_of_handle = self.alias_of.handle
        info_dict = None
        if self.glossary:
            info_dict = {
                "title": self.glossary.title,
                "text": self.glossary.text,
                "authors": [a.dict_format() for a in self.glossary.authors.all()],
                "summary": self.glossary.summary(max_len=480),
            }
        return {
            "handle": self.handle,
            "type": self.type,
            "type_name": dict(self.TAG_TYPES)[self.type],
            "alias_of": alias_of_handle,
            "info": info_dict,
            "summary": self.description,
            "get_absolute_url": self.get_absolute_url(),
        }

    def __str__(self):
        s = dict(self.TAG_TYPES)[self.type] + ":" + self.handle
        if self.alias_of:
            s += " > " + self.alias_of.handle
        return s

    def get_absolute_url(self):
        return "/tag/" + str(self.handle)

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):
        if not created:
            return

        try:
            page_info = wikipedia.page(
                instance.handle, auto_suggest=True, redirect=True
            )
            url = "https://en.wikipedia.org/?curid=" + page_info.pageid
            if not instance.description:
                instance.description = wikipedia.summary(instance.handle, sentences=1)
            instance.info_link = url
        except:
            pass

        instance.save()

    class Meta:
        ordering = ["type", "handle"]


class Template(models.Model):
    type = models.CharField(max_length=1, choices=ITEM_TYPES, primary_key=True)
    template = ck_field.RichTextUploadingField(verbose_name="Text")

    def __str__(self):
        return dict(ITEM_TYPES)[self.type] + " template"

    def __repr__(self):
        return dict(ITEM_TYPES)[self.type] + " template"


class Community(models.Model):
    # The name of the community
    name = models.CharField(max_length=254,
                            verbose_name="community")
    # abbreviation = models.CharField(max_length=50, blank=True, null=True,
    #                                default=None)
    # Communities are hierarchical
    part_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="subcommunities",
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Community(%s)" % (self.name,)

    def get_parents(self):
        if self.part_of is not None:
            return [self.part_of] + self.part_of.get_parents()
        return []

    class Meta:
        verbose_name_plural = "communities"


class Link(models.Model):
    from_item = models.ForeignKey("Item", on_delete=models.CASCADE, related_name="+")
    to_item = models.ForeignKey("Item", on_delete=models.CASCADE, related_name="+")

    def __str__(self):
        return "%s -> %s" % (str(self.from_item), str(self.to_item))

    def save(self, *args, **kwargs):
        reflexive = True if self.pk is None else False
        super(Link, self).save(*args, **kwargs)

        # Make link reflexive
        if reflexive:
            self.to_item.link(self.from_item)

    class Meta:
        verbose_name_plural = "links"


class Item(models.Model):
    draft = models.BooleanField(default=True)
    # Tags linked to this item
    tags = models.ManyToManyField("Tag", blank=True)
    # The other items that are linked to this item
    links = models.ManyToManyField(
        "Item", blank=True, through="Link", symmetrical=False
    )
    # The comments linked to this item
    comments = models.ManyToManyField("Comment", blank=True, editable=True)
    # Whether this item is featured by a moderator
    featured = models.BooleanField(default=False)
    # The type of this item, important to know which subclass to load
    type = models.CharField(max_length=1, choices=ITEM_TYPES, editable=False)
    # The score of this item, which can be used for ranking of search results
    score = models.IntegerField(default=0)
    # The date that this item was created in the database
    create_date = models.DateTimeField(auto_now_add=True, editable=False)
    # The concatenated string representation of each item for free text search
    searchablecontent = models.TextField(editable=False)
    # The communities for which the item is visible
    communities = models.ManyToManyField("Community", related_name="items")

    @property
    def authors(self):
        return ItemAuthor.objects.filter(item=self)

    # Return reference the proper subclass when possible, else return None
    def downcast(self):
        # Define links to subclasses
        subcls = {
            "P": lambda self: self.person,
            "G": lambda self: self.goodpractice,
            "I": lambda self: self.information,
            "R": lambda self: self.project,
            "E": lambda self: self.event,
            "Q": lambda self: self.question,
            "S": lambda self: self.glossary,
            "U": lambda self: self.usercase,
        }
        # If link to the current subclass is known
        if self.type in subcls:
            return subcls[self.type](self)
        else:
            return None

    def save(self, *args, **kwargs):
        # If new instance is created, set the default community (public)
        super(Item, self).save(*args, **kwargs)
        if self.pk is None:
            self.communities.add(Community.objects.get(pk=1))

    @property
    def display_name(self):
        return self.__str__()

    def summary(self):
        return ""

    def link(self, link):
        Link.objects.get_or_create(from_item=self, to_item=link)

    def _truncate(self, text, max_len=200):
        if len(text) > max_len:
            return strip_tags(text)[: max_len - 2] + "..."
        return strip_tags(text)

    # Dictionary representation used to communicate the model to the client
    def dict_format(self, obj=None):
        # Fill dict format at this level
        # make sure the pass by reference does not cause unexpected results
        if obj is None:
            obj = {}
        obj = obj.copy()
        obj.update(
            {
                "id": self.id,
                "type": dict(ITEM_TYPES)[self.type],
                "tags": [t.dict_format() for t in list(self.tags.all())],
                "featured": self.featured,
                "score": self.score,
                "summary": self.summary(),
                "create_date": self.create_date,
                "named-authors": [a.person.dict_format() for a in self.authors],
                "get_absolute_url": self.downcast().get_absolute_url(),
            }
        )
        # Attempt to get reference to subclass
        subcls = self.downcast()
        # Attempt to let subclasses fill in dict format further
        if subcls is not None and hasattr(subcls, "dict_format"):
            return subcls.dict_format(obj)
        else:
            return obj

    def get_absolute_url(self):
        if self.type in dict(ITEM_TYPES):
            t = dict(ITEM_TYPES)[self.type].lower().replace(" ", "")
            return "/" + t + "/" + str(self.id)
        else:
            return "/item/" + str(self.id)

    def __str__(self):
        # Attempt to get reference to subclass
        subcls = self.downcast()
        if subcls is not None:
            return subcls.__str__()
        else:
            return self.searchablecontent[:40]

    def save_dupe(self):
        super(Item, self).save()


class Comment(models.Model):
    tags = models.ManyToManyField(Tag, blank=True)
    text = ck_field.RichTextUploadingField()
    author = models.ForeignKey("Person", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    upvoters = models.ManyToManyField("Person", related_name="upvoters", blank=True)
    downvoters = models.ManyToManyField("Person", related_name="downvoters", blank=True)

    def __str__(self):
        return str(
            self.text[:40],
        )

    @property
    def votes(self):
        return self.upvoters.all().count() - self.downvoters.all().count()

    def summary(self):
        return self._truncate(self.text)


class Person(Item):
    # Handle to identify this person with
    handle = models.CharField(max_length=255)
    # The official title, e.g. `dr.' or `prof.'
    title = models.CharField(max_length=50, blank=True, default="")
    # The full name of this person, including first names and family name
    name = models.CharField(max_length=254)
    # Short text describing the core of this person
    headline = models.CharField(max_length=200, blank=True, null=True)
    # Text describing this person
    about = ck_field.RichTextUploadingField(blank=True, null=True)
    # The source of a photo
    photo = models.ImageField(upload_to="profile_pictures", blank=True, null=True)
    # The website of this person
    website = models.URLField(max_length=255, null=True, blank=True)
    # The email address of this person
    email = models.EmailField(null=True)
    # User corresponding to this person. If user deleted, person remains.
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    # The ID given by some external auth-service
    external_id = models.CharField(max_length=255, null=True, blank=True)

    # Show the email addres on public pages
    public_email = models.BooleanField(default=False, verbose_name="Make email public")

    # University of the user provided on registry
    university = models.CharField(max_length=500)

    # Optional introduction given by the user on registry
    introduction = models.TextField(null=True, blank=True)

    is_ghost = models.BooleanField(
        default=False, verbose_name="Make this author anonymous"
    )

    class Meta:
        ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super(Person, self).__init__(*args, **kwargs)
        self.type = "P"

    def summary(self):
        return self.headline

    @property
    def display_name(self):
        return self.name

    def display_handle(self):
        return "@%s" % (self.handle,)

    display_handle.short_description = "Handle"

    def dict_format(self, obj=None):
        """Dictionary representation used to communicate the model to the
        client.
        """
        if obj is None:
            return super(Person, self).dict_format()
        else:
            obj.update(
                {
                    "handle": self.handle,
                    "title": self.title,
                    "name": self.name,
                    "about": self.about,
                    "photo": self.photo,
                    "website": self.website,
                    "summary": self.summary(),
                    "email": self.email,
                    "is_ghost": self.is_ghost,
                }
            )
            return obj

    def __str__(self):
        return "[Person] %s" % (self.name,)

    def save(self, *args, **kwargs):
        texts = [
            cleanup_for_search(self.name),
            cleanup_for_search(self.about),
            cleanup_for_search(self.headline),
        ]
        self.searchablecontent = "<br />".join(texts)
        super(Person, self).save(*args, **kwargs)


class TextItem(Item):
    # The title of the good practice
    title = models.CharField(max_length=255)
    # The WYSIWYG text of the good practice
    text = ck_field.RichTextUploadingField(verbose_name="Text")
    # The person who created the good practice
    authors = models.ManyToManyField(Person)

    def display_author(self):
        if authors := self.authors.all():
            return ", ".join([a.name for a in authors])

        return "<No author>"

    display_author.short_description = "Author"

    class Meta:
        abstract = True

    def summary(self, max_len=200):
        return self._truncate(self.text, max_len=max_len)

    def dict_format(self, obj=None):
        """Dictionary representation used to communicate the model to the
        client.
        """
        if obj is None:
            return super(self.__class__, self).dict_format()
        else:
            # make sure the pass by reference does not cause unexpected results
            obj = obj.copy()
            obj.update(
                {
                    "authors": [a.dict_format() for a in self.authors.all()],
                    "title": self.title,
                    "summary": self.summary(),
                    "text": self.text,
                }
            )
            return obj

    def __str__(self):
        return "[%s] %s" % (dict(ITEM_TYPES)[self.type], self.title)

    @property
    def display_name(self):
        return self.title

    def save(self, *args, **kwargs):
        self.title = self.title.strip()
        self.searchablecontent = "<br />".join(
            [cleanup_for_search(self.title), cleanup_for_search(self.text)]
        )
        # On create, not update
        if self.pk is None:
            super(TextItem, self).save(*args, **kwargs)

        # Add self to author links and vica versa
        for author in [a for a in self.authors.all() if self not in a.links.all()]:

            author.link(self)
            author.save()

            self.link(author)

        super(TextItem, self).save(*args, **kwargs)


class GoodPractice(TextItem):
    def __init__(self, *args, **kwargs):
        super(GoodPractice, self).__init__(*args, **kwargs)
        self.type = "G"


class Information(TextItem):
    def __init__(self, *args, **kwargs):
        super(Information, self).__init__(*args, **kwargs)
        self.type = "I"


class CpdActivity(models.Model):
    def __init__(self, *args, **kwargs):
        super(CpdActivity, self).__init__(*args, **kwargs)
        self.type = "U"

    # The person who can be contacted for more info on the project
    user_case = models.ForeignKey(
        "UserCase", on_delete=models.CASCADE, related_name="+"
    )

    def dict_format(self, obj=None):
        """Dictionary representation used to communicate the model to the
        client.
        """
        if obj is None:
            return super(CpdActivity, self).dict_format()
        else:
            # make sure the pass by reference does not cause unexpected results
            obj = obj.copy()
            obj.update(
                {
                    "authors": [a.dict_format() for a in self.authors.all()],
                    "title": self.title,
                    "text": self.text,
                    "summary": self.summary(),
                    "contact": self.contact.dict_format(),
                    "begin_date": self.begin_date,
                    "end_date": self.end_date,
                }
            )
            return obj


class UserCase(TextItem):
    def __init__(self, *args, **kwargs):
        super(UserCase, self).__init__(*args, **kwargs)
        self.type = "U"

    def get_cpd_scenario(self):
        return CPDScenario.from_usercase(self.id)

    wallpaper = models.ImageField(upload_to="user_cases", blank=True, null=True)

    context_goals = ck_field.RichTextUploadingField(verbose_name="Context and Goals")

    cpd_activities = ck_field.RichTextUploadingField(verbose_name="CPD Activities")

    cpd_questions = models.ManyToManyField(
        "CPDQuestion",
        blank=True,
        related_name="cpd_questions",
    )

    cpd_time_to_finish = models.ForeignKey(
        "CPDTimeToFinish",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="cpd_time_to_finish",
    )

    cpd_learning_environment = models.ManyToManyField(
        "CPDLearningEnvironment",
        blank=True,
        related_name="cpd_learning_environment",
    )

    evaluation = ck_field.RichTextUploadingField(verbose_name="Evaluation")

    def save(self, *args, **kwargs):
        super(UserCase, self).save(*args, **kwargs)

        # delete all relations with CPD tags
        cpd_tags = self.tags.all().filter(type=Tag.TT_CPD)
        for cpd_tag in cpd_tags:
            self.tags.remove(cpd_tag)

        # reconstruct CPD tag relations
        cpd_scales = [q.scale.label for q in self.cpd_questions.all()]
        cpd_tags = Tag.objects.all().filter(type=Tag.TT_CPD, handle__in=cpd_scales)
        for cpd_tag in cpd_tags:
            self.tags.add(cpd_tag)

    def context_and_goals(self):
        competences = []
        attitudes = []
        activities = []

        for question in self.cpd_questions.all():
            if (question.scale.scale_type == "P1"):
                competences.append(f"{question.question_nr} {question.question}")
            elif (question.scale.scale_type == "P2"):
                attitudes.append(f"{question.question_nr} {question.question}")
            elif (question.scale.scale_type == "P3"):
                activities.append(f"{question.question_nr} {question.question}")
        return competences, attitudes, activities

    def dict_format(self, obj=None):
        """Dictionary representation used to communicate the model to the
        client.
        """
        if obj is None:
            return super(self.__class__, self).dict_format()
        else:
            # make sure the pass by reference does not cause unexpected results
            obj = obj.copy()
            obj.update(
                {
                    "wallpaper": self.wallpaper,
                    "authors": [a.dict_format() for a in self.authors.all()],
                    "title": self.title,
                    "summary": self.summary(),
                    "text": self.text,
                }
            )
            return obj


class Project(TextItem):
    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        self.type = "R"

    # The person who can be contacted for more info on the project
    contact = models.ForeignKey("Person", on_delete=models.CASCADE, related_name="+")
    # The begin date of the project
    begin_date = models.DateTimeField(auto_now=True, editable=True)
    # The end date of the project
    end_date = models.DateTimeField(auto_now=True, editable=True)

    def dict_format(self, obj=None):
        """Dictionary representation used to communicate the model to the
        client.
        """
        if obj is None:
            return super(Project, self).dict_format()
        else:
            # make sure the pass by reference does not cause unexpected results
            obj = obj.copy()
            obj.update(
                {
                    "authors": [a.dict_format() for a in self.authors.all()],
                    "title": self.title,
                    "text": self.text,
                    "summary": self.summary(),
                    "contact": self.contact.dict_format(),
                    "begin_date": self.begin_date,
                    "end_date": self.end_date,
                }
            )
            return obj


class Event(TextItem):
    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self.type = "E"

    # The person who can be contacted for more info on the project
    contact = models.ForeignKey("Person", on_delete=models.CASCADE, related_name="+")
    # The date of the event
    date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, default="")

    @property
    def is_past_due(self):
        t = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
        if t > self.date:
            return True
        return False

    def dict_format(self, obj=None):
        """Dictionary representation used to communicate the model to the
        client.
        """
        if obj is None:
            return super(Event, self).dict_format()
        else:
            obj.update(
                {
                    "authors": [a.dict_format() for a in self.authors.all()],
                    "title": self.title,
                    "text": self.text,
                    "is_past_due": self.is_past_due,
                    "location": self.location,
                    "summary": self.summary(),
                    "contact": self.contact.dict_format(),
                    "date": self.date,
                }
            )
            return obj


class Question(TextItem):
    def __init__(self, *args, **kwargs):
        super(Question, self).__init__(*args, **kwargs)
        self.type = "Q"

    def __str__(self):
        return "[Question] %s" % (self.title,)


class Glossary(TextItem):
    def __init__(self, *args, **kwargs):
        super(Glossary, self).__init__(*args, **kwargs)
        self.type = "S"


# Queries can be stored to either be displayed on the main page, rss feed or to
# allow persons to subscribe to the query in order to be notified if the
# results are updated (i.e. new results can be found).
class SearchQuery(models.Model):
    # Which tags are mentioned in the query
    tags = models.ManyToManyField(Tag, related_name="in_queries")
    # Which persons are mentioned in the query
    persons = models.ManyToManyField(Person, related_name="in_queries")
    # What was the last known (cached) result of this query
    result = models.ManyToManyField(Item, related_name="result_of")
    # When was the query stored
    stored = models.DateTimeField(auto_now=True)


# Subscriptions indicate to update the reader if results of a query change
class Subscription(models.Model):
    # What query is subscribed to?
    query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, null=False)
    # Who is subscribing to this query (to contact this person later)
    reader = models.ForeignKey(Person, on_delete=models.CASCADE, null=False)


# DisplayQueries indicate to show the query on the homepage
class DisplayQuery(models.Model):
    # The query that is displayed
    query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, null=False)
    # The template to use when rendering
    template = models.CharField(max_length=100)


class ItemAuthor(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="author_item")
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="author_person"
    )
    status = models.CharField(
        max_length=100,
        default="PENDING",
        choices=(
            ("ACCEPTED", "ACCEPTED"),
            ("PENDING", "PENDING"),
            ("DECLINED", "DECLINED"),
        ),
    )

    def __str__(self):
        return str(self.item) + " " + str(self.person) + " (" + self.status + ")"


post_save.connect(Tag.post_create, sender=Tag)
