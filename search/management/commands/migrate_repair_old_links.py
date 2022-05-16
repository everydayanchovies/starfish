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
        parser.add_argument("path_to_db", type=str)

    def handle(self, *args, **options):
        # Create backup of existing database
        path_to_db = options["path_to_db"]
        shutil.copyfile(path_to_db, path_to_db + "_pre_datarestoration_backup_" + datetime.now().strftime("%m.%d.%Y_%H.%M.%S"))

        for obj_class in [Glossary, Event, GoodPractice, Information, Project, Question]:
            for obj in obj_class.objects.all():
                print("Repairing " + str(obj))
                obj.text = self.repair_links_in_text(obj.text)
                obj.save()

    def repair_links_in_text(self, text):
        text = text.replace("https://www.starfish.innovatievooronderwijs.nl/", "/")
        text = text.replace("https://starfish.innovatievooronderwijs.nl/", "/")
        text = text.replace("http://www.starfish.innovatievooronderwijs.nl/", "/")
        text = text.replace("http://starfish.innovatievooronderwijs.nl/", "/")
        text = text.replace("www.starfish.innovatievooronderwijs.nl/", "/")
        text = text.replace("starfish.innovatievooronderwijs.nl/", "/")
        return text
