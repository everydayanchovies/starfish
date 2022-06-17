# Generated by Django 3.2.12 on 2022-06-13 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0002_person_is_ghost'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='authors',
            field=models.ManyToManyField(to='search.Person'),
        ),
        migrations.AddField(
            model_name='glossary',
            name='authors',
            field=models.ManyToManyField(to='search.Person'),
        ),
        migrations.AddField(
            model_name='goodpractice',
            name='authors',
            field=models.ManyToManyField(to='search.Person'),
        ),
        migrations.AddField(
            model_name='information',
            name='authors',
            field=models.ManyToManyField(to='search.Person'),
        ),
        migrations.AddField(
            model_name='project',
            name='authors',
            field=models.ManyToManyField(to='search.Person'),
        ),
        migrations.AddField(
            model_name='question',
            name='authors',
            field=models.ManyToManyField(to='search.Person'),
        ),
        migrations.AddField(
            model_name='usercase',
            name='authors',
            field=models.ManyToManyField(to='search.Person'),
        ),
        migrations.AlterField(
            model_name='person',
            name='is_ghost',
            field=models.BooleanField(default=False, verbose_name='Make this author anonymous'),
        ),
    ]
