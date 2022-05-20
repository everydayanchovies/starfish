from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import shutil
from datetime import datetime

from search.models import (
    Person,
    Item
)


class Command(BaseCommand):
    dumps = {}
    dumps_as_objs = {}

    def add_arguments(self, parser):
        parser.add_argument("path_to_dumps", type=str)
        parser.add_argument("path_to_db", type=str)

    def handle(self, *args, **options):
        dump_filenames = [
            "export_person",  # item_ptr_id name
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

    def arr_to_person(self, arr):
        item_ptr_id, name = arr
        return (item_ptr_id, -1, Person(
            id=item_ptr_id,
            name=name,
        ))

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

    """
    BEGIN import object
    """

    def import_items(self, table_name, item_class, equality_fn):
        added_item_ids = []

        live_items = item_class.objects.all()
        for i, (old_id, new_id, oi) in enumerate(self.dumps_as_objs[table_name]):
            for oj in live_items:
                if equality_fn(oi, oj):
                    self.dumps_as_objs[table_name][i] = (old_id, oj.id, oj)
                    break
            else:
                print("Adding item " + str(oi))
                oi.save()
                added_item_ids.append(oi.id)
                self.dumps_as_objs[table_name][i] = (old_id, oi.id, oi)

        print("Added: ", set(added_item_ids))

    def import_person(self):
        self.import_items(
            "export_person",
            Person,
            lambda a, b: a.name == b.name
        )

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
