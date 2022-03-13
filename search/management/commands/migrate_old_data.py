from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from search.models import Project, Person, Community


# TODO:
# * load pg dump data into arrays
# * import data from arrays
# * dry run again with fresh db backup from production
# * create another backup and execute on production
class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path", type=str)

    def handle(self, *args, **options):
        dump_filenames = [
            "export_person",  # item_ptr_id name
            "search_community",  # id name part_of_id
            "search_event",  # item_ptr_id title text date location author_id contact_id
            "search_glossary",  # item_ptr_id title text author_id
            "search_goodpractice",  # item_ptr_id title text author_id
            "search_information",  # item_ptr_id title text author_id
            "search_item_tags",  # id item_id tag_id
            "search_project",  # item_ptr_id title text begin_date end_date author_id contact_id
            "search_question",  # item_ptr_id title text author_id
            "search_tag",  # id type handle alias_of_id glossary_id
        ]

        dumps = {}
        for filename in dump_filenames:
            dumps[filename] = self.sql_to_strings(
                options["path"] + "/" + filename + ".sql"
            )

        print(dumps["search_community"])

    def sql_to_strings(self, filepath):
        lines = []

        with open(filepath, "r") as f:
            while not f.readline().startswith("COPY"):
                pass

            while line := f.readline():
                data = line.strip().split("\t")

                if len(lines) > 0 and len(lines[0]) != len(data):
                    break

                data = map(self.clean_data, data)
                lines.append(data)

        return lines

    def clean_data(self, data):
        if data == "\\N":
            return None

        return data
