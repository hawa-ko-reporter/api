# Generated by Django 3.0.5 on 2020-07-20 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0002_program'),
    ]

    operations = [
        migrations.RenameField(
            model_name='program',
            old_name='title',
            new_name='name',
        ),
    ]