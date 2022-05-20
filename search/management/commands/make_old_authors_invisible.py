from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import shutil
from datetime import datetime

from search.models import (
    Person,
)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("path_to_db", type=str)

    def handle(self, *args, **options):
        # Create backup of existing database
        path_to_db = options["path_to_db"]
        shutil.copyfile(path_to_db, path_to_db + "_pre_datarestoration_backup_" + datetime.now().strftime("%m.%d.%Y_%H.%M.%S"))

        old_authors = [2, 644, 646, 650, 42, 563, 311, 842, 331, 203, 459, 849, 744, 361, 755, 503, 505, 635, 764]

        for old_author_id in old_authors:
            author = Person.objects.get(id=old_author_id)
            author.is_ghost = True
            author.save()
