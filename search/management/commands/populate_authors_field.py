from django.core.management.base import BaseCommand
import shutil
from datetime import datetime
from search.models import (
    Person,
    GoodPractice,
    Information,
    UserCase,
    Project,
    Event,
    Question,
    Glossary,
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path_to_db", type=str)

    def handle(self, *args, **options):
        # Create backup of existing database
        path_to_db = options["path_to_db"]
        shutil.copyfile(
            path_to_db,
            path_to_db
            + "_pre_populate_authors_field_backup_"
            + datetime.now().strftime("%m.%d.%Y_%H.%M.%S"),
        )

        for c in [
            GoodPractice,
            Information,
            UserCase,
            Project,
            Event,
            Question,
            Glossary,
        ]:
            for item in c.objects.all():
                if not item.authors.all():
                    item.authors.add(item.author)
                    item.save()
