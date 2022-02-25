from django.contrib import admin
from django import forms
from search.models import *
from search.widgets import TagInput


class QuerySetMock(object):
    def __init__(self, l, qs):
        self.l = l
        self.qs = qs

    def __getattribute__(self, key):
        if key == "all" or key == "l":
            return super(QuerySetMock,self).__getattribute__(key)
        else:
            qs = super(QuerySetMock,self).__getattribute__('qs')
            return qs.__getattribute__(key)

    def all(self):
        return self.l


class LinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_item', 'to_item')


class LinkInline(admin.TabularInline):
    model = Link
    fk_name='from_item'

    def get_formset(self, request, obj=None, **kwargs):
        fs = super(LinkInline, self).get_formset(request, obj, **kwargs)
        qs = fs.form.base_fields['to_item'].queryset
        #links = sorted(qs, key=(
        #    lambda x: (x.type, x.downcast().name.strip().split(" ")[-1]
        #    if x and x.type == "P" else x.downcast().title)))
        fs.form.base_fields['to_item'].queryset = qs
        return fs

class ItemAdmin(admin.ModelAdmin):
    filter_horizontal = ('links',)
    inlines = (LinkInline,)

    def response_add(self, request, obj, post_url_continue=None):
        # Additional save necessary to store new connections in save method
        obj.save()
        return super(ItemAdmin, self).response_add(request, obj,
                                                   post_url_continue)

    def response_change(self, request, obj):
        # Additional save necessary to store new connections in save method
        obj.save()
        return super(ItemAdmin, self).response_change(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ItemAdmin, self). get_form(request, obj, **kwargs)

        if 'author' in form.base_fields:
            qs = form.base_fields['author'].queryset
            persons = sorted(qs, key=(lambda x:
                x.downcast().name.strip().split(" ")[-1]))
            form.base_fields['author'].queryset = qs
        if 'contact' in form.base_fields:
            qs = form.base_fields['contact'].queryset
            persons = sorted(qs, key=(lambda x:
                x.downcast().name.strip().split(" ")[-1]))
            form.base_fields['contact'].queryset = qs
        return form


class PersonAdmin(ItemAdmin):
    list_display = ('display_handle', 'name')
    search_fields = ('handle', 'name')


class TextItemAdmin(ItemAdmin):
    list_display = ('title', 'display_author', 'create_date')
    search_fields = ('title',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('handle','alias_of', 'glossary')
    search_fields = ('handle',)
    list_filter = ('type',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "alias_of":
            kwargs["queryset"] = Tag.objects.filter(alias_of=None)
        s = super(TagAdmin, self)
        return s.formfield_for_foreignkey(db_field, request, **kwargs)


class TaggableItemAdmin(ItemAdmin):
    def formfield_for_manytomany(self, db_field, request, **kwargs):
#        if db_field.name == "tags":
#            kwargs["widget"] = TagInput()
        s = super(TaggableItemAdmin, self)
        return s.formfield_for_manytomany(db_field, request, **kwargs)

class GlossaryAdmin(TextItemAdmin):
    actions = ['duplicate_as_info']

    def duplicate_as_info(self, request, queryset):
        for glossary in queryset:
            try:
                info = Information(
                        title=glossary.title,
                        text=glossary.text,
                        author=glossary.author,
                        featured=glossary.featured,
                        score=glossary.score)
                info.save()
                for comment in glossary.comments.all():
                    info.comments.add(comment)
                for tag in glossary.tags.all():
                    info.tag(tag)
                for link in glossary.links.all():
                    info.link(link)
                info.links.add(glossary)
                info.save()
                self.message_user(
                        request,
                        "%s was succesfully duplicated." % (glossary.title, ))
            except Exception as e:
                self.message_user(
                        request,
                        "%s could not be duplicated." % (glossary.title, ),
                        "error")
    duplicate_as_info.short_description = \
            "Duplicate selected glossaries as information"


admin.site.register(Person, PersonAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(GoodPractice, TaggableItemAdmin)
admin.site.register(Information, TextItemAdmin)
admin.site.register(Project, TextItemAdmin)
admin.site.register(Event, TextItemAdmin)
admin.site.register(Question, TextItemAdmin)
admin.site.register(UserCase, TaggableItemAdmin)
admin.site.register(Comment)
admin.site.register(Community)
admin.site.register(Glossary, GlossaryAdmin)
admin.site.register(Template)
admin.site.register(Link, LinkAdmin)
admin.site.register(Item)
admin.site.register(ItemAuthor)
