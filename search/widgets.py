from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import widgets

from search.models import Tag
from search.signals import unknown_tag_signal
from search.utils import parse_tags

SEARCH_SETTINGS = settings.SEARCH_SETTINGS


class TagInput(widgets.Widget):
    class Media:
        js = ('jquery-ui.min.js', 'tag-it.js', 'tagit_search_input.js')
        css = {'all': ('jquery-ui-1.10.3.custom.css', 'jquery.tagit.css')}

    def render(self, name, value, attrs=None, renderer=None):
        # final_attrs = self.build_attrs(attrs)
        tid = "id_" + name
        delim = SEARCH_SETTINGS['syntax']['DELIM']
        tsymb = SEARCH_SETTINGS['syntax']['TAG']
        if value is None:
            value = ''
        else:
            value = delim.join([tsymb + t.handle for t in
                                Tag.objects.filter(id__in=value)])
        script = "<script type='text/javascript'>"
        script += "$(function(){make_tagit(\"%s\",\"%s\");})" % (tid, delim)
        script += "</script>"
        return script + "<input class='form-control' type='text' " + \
               "name='%s' id='%s' value='%s' />" % (name, tid, value)

    def value_from_datadict(self, data, files, name):
        raw_value = data.get(name, None)
        if raw_value is not None:
            tags, unknown_tags = parse_tags(raw_value)
            if unknown_tags['token'] or unknown_tags['person'] or \
                    unknown_tags['literal']:
                print(data)
                unknown_tag_signal.send(sender=self, author=data['author'],
                                        title=data['title'], tags=unknown_tags)
            return [tag.id for tag in tags]
        else:
            return None


class NonAdminFilteredSelectMultiple(FilteredSelectMultiple):
    @property
    def media(self):
        media = super(NonAdminFilteredSelectMultiple, self).media
        return media
