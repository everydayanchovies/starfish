import pgdumplib
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from search.models import Project, Person, Community


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        saw_copy = False

        for p in Project.objects.all():
            p.delete()
        print("deleted all projects")

        with open(options['path'], "r") as f:
            while not saw_copy:
                line = f.readline()
                if line.startswith("COPY"):
                    saw_copy = True
                    break

            # item_ptr_id, title, text, begin_date, end_date, author_id, contact_id
            line = f.readline()
            authors = []
            contacts = []

            while line:
                data = line.strip().split("\t")
                if (len(data) != 7): break
                authors += [data[5]]
                contacts += [data[6]]

                line = f.readline()

                print(data[:2])
                print(data[3:])
                print(Person.objects.all())


                project = Project(
                    draft=False,
                    title=data[1],
                    text=data[2].replace("\\n", "").replace("\\r", "").replace("\\t", ""),
                    author=Person.objects.first(),
                    contact=Person.objects.first(),
                    begin_date=data[3],
                    end_date=data[4],
                )
                project.save()
                project.communities.set(Community.objects.filter(name="Public"))
                project.save()


            print(set(authors), set(contacts))
        self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % 1))