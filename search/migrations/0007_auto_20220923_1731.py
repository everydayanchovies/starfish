# Generated by Django 3.2.12 on 2022-09-23 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0006_cpdquestion_question_nr'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='community',
            options={'verbose_name_plural': 'communities'},
        ),
        migrations.AlterField(
            model_name='community',
            name='name',
            field=models.CharField(max_length=254, verbose_name='community'),
        ),
    ]