# Generated by Django 3.2.12 on 2022-09-21 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0005_cpd'),
    ]

    operations = [
        migrations.AddField(
            model_name='cpdquestion',
            name='question_nr',
            field=models.IntegerField(default=0),
        ),
    ]