from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from search.models import (
    Project,
    Person,
    Community,
    Event,
    Glossary,
    GoodPractice,
    Information,
    Question,
    Tag,
)


# TODO:
# * import data from arrays
# * dry run again with fresh db backup from production
# * create another backup and execute on production
class Command(BaseCommand):
    dumps = {}
    dumps_as_objs = {}

    def add_arguments(self, parser):
        parser.add_argument("path", type=str)

    def handle(self, *args, **options):
        # Order matters! Person and glossary must be the first and second entries in this array.
        dump_filenames = [
            "export_person",  # item_ptr_id name
            "search_glossary",  # item_ptr_id title text author_id
            "search_community",  # id name part_of_id
            "search_event",  # item_ptr_id title text date location author_id contact_id
            "search_goodpractice",  # item_ptr_id title text author_id
            "search_information",  # item_ptr_id title text author_id
            "search_item_tags",  # id item_id tag_id
            "search_project",  # item_ptr_id title text begin_date end_date author_id contact_id
            "search_question",  # item_ptr_id title text author_id
            "search_tag",  # id type handle alias_of_id glossary_id
        ]

        for filename in dump_filenames:
            self.dumps[filename] = self.sql_to_strings(
                options["path"] + "/" + filename + ".sql"
            )

        for filename in dump_filenames:
            fn = "arr_to_" + filename.replace("search_", "").replace("export_", "")
            print("Executing " + fn)
            if not hasattr(self, fn):
                continue
            self.dumps_as_objs[filename] = filter(
                None, list(map(getattr(self, fn), self.dumps[filename]))
            )

        for filename in dump_filenames:
            fn = "import_" + filename.replace("search_", "").replace("export_", "")
            print("Executing " + fn)
            if not hasattr(self, fn):
                continue
            getattr(self, fn)()

    def sql_to_strings(self, filepath):
        lines = []

        with open(filepath, "r") as f:
            while not f.readline().startswith("COPY"):
                pass

            while line := f.readline():
                data = line.strip().split("\t")

                if len(lines) > 0 and len(lines[0]) != len(data):
                    break

                data = list(map(self.clean_data, data))
                lines.append(data)

        return lines

    def clean_data(self, data):
        if data == "\\N":
            return None

        return data

    """
    BEGIN array to object
    """

    def arr_to_project(self, arr):
        item_ptr_id, title, text, begin_date, end_date, author_id, contact_id = arr
        author = self.person_for_id(author_id)
        contact = self.person_for_id(contact_id)
        if not author or not contact:
            return None
        return Project(
            draft=False,
            title=title,
            text=text,
            author=author,
            contact=contact,
            begin_date=begin_date,
            end_date=end_date,
        )

    def arr_to_person(self, arr):
        item_ptr_id, name = arr
        return Person(
            id=item_ptr_id,
            name=name,
        )

    def arr_to_community(self, arr):
        cid, name, part_of_id = arr
        return Community(
            name=name,
            part_of_id=part_of_id,
        )

    def arr_to_event(self, arr):
        item_ptr_id, title, text, date, location, author_id, contact_id = arr
        author = self.person_for_id(author_id)
        contact = self.person_for_id(contact_id)
        if not author or not contact:
            return None
        return Event(
            title=title,
            text=text,
            date=date,
            location=location,
            author=author,
            contact=contact,
        )

    def arr_to_glossary(self, arr):
        item_ptr_id, title, text, author_id = arr
        author = self.person_for_id(author_id)
        if not author:
            return None
        return Glossary(
            title=title,
            text=text,
            author=author,
        )

    def arr_to_goodpractice(self, arr):
        item_ptr_id, title, text, author_id = arr
        author = self.person_for_id(author_id)
        if not author:
            return None
        return GoodPractice(
            title=title,
            text=text,
            author=author,
        )

    def arr_to_information(self, arr):
        item_ptr_id, title, text, author_id = arr
        author = self.person_for_id(author_id)
        if not author:
            return None
        return Information(
            title=title,
            text=text,
            author=author,
        )

    def arr_to_question(self, arr):
        item_ptr_id, title, text, author_id = arr
        author = self.person_for_id(author_id)
        if not author:
            return None
        return Information(
            title=title,
            text=text,
            author=author,
        )

    def arr_to_tag(self, arr):
        tid, ttype, handle, alias_of_id, glossary_id = arr
        glossary = self.glossary_for_id(glossary_id)
        if not glossary:
            return None
        return Tag(
            type=ttype,
            handle=handle,
            alias_of_id=alias_of_id,
            glossary=glossary,
        )

    """
    END array to object
    """

    def person_for_id(self, pid):
        parrs = [x for x in self.dumps["export_person"] if x[0] == pid]
        if not parrs:
            print("Warning! No person found for pid " + pid)
            return None

        pliveobjs = [x for x in Person.objects.all() if x.name == parrs[0][1]]
        if not pliveobjs:
            return None

        print("Warning! No person found in objs for pid " + pid)

        return pliveobjs[0]

    def glossary_for_id(self, gid):
        if not gid:
            print("Warning! Attempting to get glossary with None id")
            return None

        garrs = [x for x in self.dumps["search_glossary"] if x[0] == gid]
        if not garrs:
            print("Warning! No glossary found for gid " + gid)
            return None

        gliveobjs = [x for x in Glossary.objects.all() if x.title == garrs[0][1]]
        if not gliveobjs:
            return None

        print("Warning! No glossary found in objs for gid " + gid)

        return gliveobjs[0]

    """
    BEGIN import object
    """

    def import_project(self):
        live_projects = Project.objects.all()
        for oi in self.dumps_as_objs["search_project"]:
            for oj in live_projects:
                if oi.title == oj.title:
                    break
            else:
                print("Adding project " + oi.title)
                oi.save()

    def import_person(self):
        live_persons = Person.objects.all()
        for pi in self.dumps_as_objs["export_person"]:
            for pj in live_persons:
                if pi.name == pj.name:
                    break
            else:
                print("Adding person " + pi.name)
                pi.save()

    def import_community(self):
        live_communities = Community.objects.all()
        for oi in self.dumps_as_objs["search_community"]:
            for oj in live_communities:
                if oi.name == oj.name:
                    break
            else:
                print("Adding community " + oi.name)
                oi.save()

    def import_event(self):
        live_events = Event.objects.all()
        for oi in self.dumps_as_objs["search_event"]:
            for oj in live_events:
                if oi.title == oj.title:
                    break
            else:
                print("Adding event " + oi.title)
                oi.save()

    def import_glossary(self):
        live_glossaries = Glossary.objects.all()
        for gi in self.dumps_as_objs["search_glossary"]:
            for gj in live_glossaries:
                if gi.title == gj.title:
                    break
            else:
                print("Adding glossary " + gi.title)
                gi.save()

    def import_goodpractice(self):
        live_gps = GoodPractice.objects.all()
        for oi in self.dumps_as_objs["search_goodpractice"]:
            for oj in live_gps:
                if oi.title == oj.title:
                    break
            else:
                print("Adding goodpractice " + oi.title)
                oi.save()

    def import_information(self):
        live_infos = Information.objects.all()
        for oi in self.dumps_as_objs["search_information"]:
            for oj in live_infos:
                if oi.title == oj.title:
                    break
            else:
                print("Adding information " + oi.title)
                oi.save()

    # TODO why does this not save?
    def import_question(self):
        live_questions = Question.objects.all()
        print(Question.objects.filter(title="Hoe berekent TestVision de cijfers?"))
        for oi in self.dumps_as_objs["search_question"]:
            for oj in live_questions:
                if oi.title == oj.title:
                    break
            else:
                print("Adding question " + oi.title)
                oi.save()
                print(Question.objects.filter(title=oi.title))

    def import_tag(self):
        live_tags = Tag.objects.all()
        for oi in self.dumps_as_objs["search_tag"]:
            for oj in live_tags:
                if oi.handle == oj.handle:
                    break
            else:
                print("Adding tag " + oi.handle)
                oi.save()

    """
    END import object
    """
