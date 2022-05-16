from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import shutil
from datetime import datetime

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
    Item
)


class Command(BaseCommand):
    dumps = {}
    dumps_as_objs = {}

    def add_arguments(self, parser):
        parser.add_argument("path_to_dumps", type=str)
        parser.add_argument("path_to_db", type=str)

    def handle(self, *args, **options):
        # Order matters! Person and glossary must be the first and second entries in this array.
        dump_filenames = [
            "export_person",  # item_ptr_id name
            "search_glossary",  # item_ptr_id title text author_id
            "search_community",  # id name part_of_id
            "search_tag",  # id type handle alias_of_id glossary_id
            "search_event",  # item_ptr_id title text date location author_id contact_id
            "search_goodpractice",  # item_ptr_id title text author_id
            "search_information",  # item_ptr_id title text author_id
            "search_project",  # item_ptr_id title text begin_date end_date author_id contact_id
            "search_question",  # item_ptr_id title text author_id
            "search_item_communities", # id item_id community_id
            "search_item_tags", # id item_id tag_id
        ]

        # Create backup of existing database
        path_to_db = options["path_to_db"]
        shutil.copyfile(path_to_db, path_to_db + "_pre_datarestoration_backup_" + datetime.now().strftime("%m.%d.%Y_%H.%M.%S"))

        for filename in dump_filenames:
            self.dumps[filename] = self.sql_to_strings(
                options["path_to_dumps"] + "/" + filename + ".sql"
            )

        for filename in dump_filenames:
            fn = "arr_to_" + filename.replace("search_", "").replace("export_", "")
            print("Executing " + fn)
            if not hasattr(self, fn):
                continue
            self.dumps_as_objs[filename] = list(filter(
                None, list(map(getattr(self, fn), self.dumps[filename]))
            ))

        for filename in dump_filenames:
            fn = "import_" + filename.replace("search_", "").replace("export_", "")
            print("Executing " + fn)
            if not hasattr(self, fn):
                continue
            getattr(self, fn)()

        for filename in dump_filenames:
            print("Imported " + str(len(self.dumps_as_objs[filename])) + " " + filename)

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

        data = data.replace("\\r\\n", "\n")
        data = data.replace("\\t", "\t")
        data = data.replace("media/uploads", "static/imported_media")
        data = data.strip()

        return data

    """
    BEGIN array to object
    """

    def arr_to_project(self, arr):
        item_ptr_id, title, text, begin_date, end_date, author_id, contact_id = arr
        author = self.person_for_id(author_id)
        return (item_ptr_id, -1, Project(
            draft=False,
            title=title,
            text=text + self.person_record_summery(author),
            author=self.get_natasa_person(),
            contact=self.get_natasa_person(),
            begin_date=begin_date,
            end_date=end_date,
        ))

    def arr_to_person(self, arr):
        item_ptr_id, name = arr
        return (item_ptr_id, -1, Person(
            id=item_ptr_id,
            name=name,
        ))

    def arr_to_community(self, arr):
        cid, name, part_of_id = arr
        return (cid, -1, Community(
            name=name,
            part_of_id=part_of_id,
        ))

    def arr_to_event(self, arr):
        item_ptr_id, title, text, date, location, author_id, contact_id = arr
        author = self.person_for_id(author_id)
        return (item_ptr_id, -1, Event(
            draft=False,
            title=title,
            text=text + self.person_record_summery(author),
            date=date,
            location=location,
            author=self.get_natasa_person(),
            contact=self.get_natasa_person(),
        ))

    def arr_to_glossary(self, arr):
        item_ptr_id, title, text, author_id = arr
        author = self.person_for_id(author_id)
        return (item_ptr_id, -1, Glossary(
            draft=False,
            title=title,
            text=text + self.person_record_summery(author),
            author=self.get_natasa_person(),
        ))

    def arr_to_goodpractice(self, arr):
        item_ptr_id, title, text, author_id = arr
        author = self.person_for_id(author_id)
        return (item_ptr_id, -1, GoodPractice(
            draft=False,
            title=title,
            text=text + self.person_record_summery(author),
            author=self.get_natasa_person(),
        ))

    def arr_to_information(self, arr):
        item_ptr_id, title, text, author_id = arr
        author = self.person_for_id(author_id)
        return (item_ptr_id, -1, Information(
            draft=False,
            title=title,
            text=text + self.person_record_summery(author),
            author=self.get_natasa_person(),
        ))

    def arr_to_question(self, arr):
        item_ptr_id, title, text, author_id = arr
        author = self.person_for_id(author_id)
        return (item_ptr_id, -1, Question(
            draft=False,
            title=title,
            text=text + self.person_record_summery(author),
            author=self.get_natasa_person(),
        ))

    def arr_to_tag(self, arr):
        tid, ttype, handle, alias_of_id, glossary_id = arr
        glossary = self.glossary_for_id(glossary_id)
        return (tid, -1, Tag(
            type=ttype,
            handle=handle,
            alias_of_id=alias_of_id,
            glossary=glossary,
        ))

    def arr_to_item_communities(self, arr):
        return (-1, -1, arr)

    def arr_to_item_tags(self, arr):
        return (-1, -1, arr)

    def person_record_summery(self, author):
        if not author:
            return ""
        return "\n\nOriginal author: " + author.name

    """
    END array to object
    """

    def person_for_id(self, pid):
        parrs = [x for x in self.dumps["export_person"] if x[0] == pid]
        if not parrs:
            print("Warning! No person found for pid " + pid)
            return None

        return Person(
            name=parrs[0][1]
        )

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

    def import_items(self, table_name, item_class, equality_fn):
        live_items = item_class.objects.all()
        for i, (old_id, new_id, oi) in enumerate(self.dumps_as_objs[table_name]):
            for oj in live_items:
                if equality_fn(oi, oj):
                    self.dumps_as_objs[table_name][i] = (old_id, oj.id, oj)
                    break
            else:
                print("Adding item " + str(oi))
                oi.save()
                self.dumps_as_objs[table_name][i] = (old_id, oi.id, oi)

    def import_project(self):
        self.import_items(
            "search_project",
            Project,
            lambda a, b: a.title == b.title
        )

    def import_person(self):
        # legally we are not allowed to import people
        # without their consent
        pass

    def import_community(self):
        self.import_items(
            "search_community",
            Community,
            lambda a, b: a.name == b.name
        )

    def import_event(self):
        self.import_items(
            "search_event",
            Event,
            lambda a, b: a.title == b.title
        )

    def import_glossary(self):
        self.import_items(
            "search_glossary",
            Glossary,
            lambda a, b: a.title == b.title
        )

    def import_goodpractice(self):
        self.import_items(
            "search_goodpractice",
            GoodPractice,
            lambda a, b: a.title == b.title
        )

    def import_information(self):
        self.import_items(
            "search_information",
            Information,
            lambda a, b: a.title == b.title
        )

    def import_question(self):
        self.import_items(
            "search_question",
            Question,
            lambda a, b: a.title == b.title
        )

    def import_tag(self):
        self.import_items(
            "search_tag",
            Tag,
            lambda a, b: a.handle == b.handle
        )

    def import_item_communities(self):
        for (_, _, sic) in self.dumps_as_objs["search_item_communities"]:
            _, item_id, community_id = sic
            item = self.get_item_by_old_id(item_id)
            community = self.get_item_by_old_id(community_id, "search_community")
            if not item or not community:
                print("Couldn't find item or community for mtm relation.")
                continue
            if isinstance(item, Community) or isinstance(item, Tag) or isinstance(item, Person):
                continue
            print("Setting mtm relation for " + str(item) + " and " + str(community))
            item.communities.add(community)

    def import_item_tags(self):
        for (_, _, sic) in self.dumps_as_objs["search_item_tags"]:
            _, item_id, tag_id = sic
            item = self.get_item_by_old_id(item_id)
            tag = self.get_item_by_old_id(tag_id, "search_tag")
            if not item:
                print("Couldn't find item for mtm relation.")
                continue
            if not tag:
                print("Couldn't find tag for mtm relation.")
                continue
            if isinstance(item, Community) or isinstance(item, Tag) or isinstance(item, Person):
                continue
            print("Setting mtm relation for " + str(item) + " and " + str(tag))
            item.tags.add(tag)

    def get_item_by_old_id(self, q_old_id, table=""):
        for (k, lst) in self.dumps_as_objs.items():
            if table and not table == k:
                continue
            for old_id, new_id, item in lst:
                if old_id == q_old_id:
                    return item

    """
    END import object
    """

    def get_natasa_person(self):
        return Person.objects.filter(name="Natasa Brouwer")[0]
