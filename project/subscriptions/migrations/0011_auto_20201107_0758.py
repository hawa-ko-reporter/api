# Generated by Django 3.0.5 on 2020-11-07 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0010_remove_subscription_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubscription',
            name='end_time',
            field=models.DateTimeField(default='2020-11-08T11:59:59+05:45'),
        ),
        migrations.AddField(
            model_name='usersubscription',
            name='start_time',
            field=models.DateTimeField(default='2020-11-08T05:00:00+05:45'),
        ),
    ]