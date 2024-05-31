from django.contrib import admin
from django.db.models import Q

# from search.models import *
from search import models


class QuerySetMock(object):
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


class LinkAdmin(admin.ModelAdmin):
    list_display = ("id", "from_item", "to_item")


class LinkInline(admin.TabularInline):
    model = models.Link
    fk_name = "from_item"

    def get_formset(self, request, obj=None, **kwargs):
        fs = super(LinkInline, self).get_formset(request, obj, **kwargs)
        qs = fs.form.base_fields["to_item"].queryset
        # links = sorted(qs, key=(
        #    lambda x: (x.type, x.downcast().name.strip().split(" ")[-1]
        #    if x and x.type == "P" else x.downcast().title)))
        fs.form.base_fields["to_item"].queryset = qs
        return fs


class ItemAdmin(admin.ModelAdmin):
    filter_horizontal = [
        "links",
        "tags",
        "communities",
    ]
    inlines = (LinkInline,)

    def response_add(self, request, obj, post_url_continue=None):
        # Additional save necessary to store new connections in save method
        obj.save()
        return super(ItemAdmin, self).response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        # Additional save necessary to store new connections in save method
        obj.save()
        return super(ItemAdmin, self).response_change(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ItemAdmin, self).get_form(request, obj, **kwargs)

        if "authors" in form.base_fields:
            self.filter_horizontal.append("authors")

            form.base_fields["authors"].queryset = (
                form.base_fields["authors"]
                .queryset.extra(select={"last_name": "substr(name, instr(name, ' ') + 1)"})
                .order_by("last_name")
            )

        if "contact" in form.base_fields:
            form.base_fields["contact"].queryset = (
                form.base_fields["contact"]
                .queryset.extra(select={"last_name": "substr(name, instr(name, ' ') + 1)"})
                .order_by("last_name")
            )

        if "cpd_questions" in form.base_fields:
            self.filter_horizontal.append("cpd_questions")

        if "cpd_learning_environment" in form.base_fields:
            self.filter_horizontal.append("cpd_learning_environment")

        return form


class PersonAdmin(ItemAdmin):
    list_display = ("display_handle", "name")
    search_fields = ("handle", "name")


class TextItemAdmin(ItemAdmin):
    list_display = ("title", "display_author", "create_date")
    search_fields = ("title",)


class TagAdmin(admin.ModelAdmin):
    list_display = ("handle", "alias_of", "glossary")
    search_fields = ("handle",)
    list_filter = ("type",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "alias_of":
            kwargs["queryset"] = models.Tag.objects.filter(alias_of=None)
        s = super(TagAdmin, self)
        return s.formfield_for_foreignkey(db_field, request, **kwargs)


class CPDScaleAdmin(admin.ModelAdmin):
    id = None

    def get_form(self, request, obj=None, **kwargs):
        # fetch own model id in database
        if obj:
            self.id = obj.id
        return super(CPDScaleAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # don't allow recursive child-parent relation
        # aka, hide self from scale_parent dropdown
        if db_field.name == "scale_parent":
            kwargs["queryset"] = models.CPDScale.objects.filter(~Q(id=self.id))
        return super(CPDScaleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ("js/admin/cpd_scale.js",)


class CPDQuestionAdmin(admin.ModelAdmin):
    pass


class CPDTimeToFinishAdmin(admin.ModelAdmin):
    pass


class CPDLearningEnvironmentAdmin(admin.ModelAdmin):
    pass


class GlossaryAdmin(TextItemAdmin):
    actions = ["duplicate_as_info"]

    def duplicate_as_info(self, request, queryset):
        for glossary in queryset:
            try:
                info = models.Information(
                    title=glossary.title,
                    text=glossary.text,
                    authors=glossary.authors,
                    featured=glossary.featured,
                    score=glossary.score,
                )
                info.save()
                for comment in glossary.comments.all():
                    info.comments.add(comment)
                for tag in glossary.tags.all():
                    info.tag(tag)
                for link in glossary.links.all():
                    info.link(link)
                info.links.add(glossary)
                info.save()
                self.message_user(request, "%s was succesfully duplicated." % (glossary.title,))
            except Exception as e:
                self.message_user(request, "%s could not be duplicated." % (glossary.title,), "error")
                print(e)

    duplicate_as_info.short_description = "Duplicate selected glossaries as information"


admin.site.register(models.Person, PersonAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.GoodPractice, ItemAdmin)
admin.site.register(models.Information, TextItemAdmin)
admin.site.register(models.Project, TextItemAdmin)
admin.site.register(models.Event, TextItemAdmin)
admin.site.register(models.Question, TextItemAdmin)
admin.site.register(models.UserCase, ItemAdmin)
admin.site.register(models.Comment)
admin.site.register(models.Community)
admin.site.register(models.Glossary, GlossaryAdmin)
admin.site.register(models.Template)
admin.site.register(models.Link, LinkAdmin)
admin.site.register(models.Item)
admin.site.register(models.ItemAuthor)
admin.site.register(models.CPDScale, CPDScaleAdmin)
admin.site.register(models.CPDQuestion, CPDQuestionAdmin)
admin.site.register(models.CPDTimeToFinish, CPDTimeToFinishAdmin)
admin.site.register(models.CPDLearningEnvironment, CPDLearningEnvironmentAdmin)
