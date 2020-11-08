# Generated by Django 3.0.5 on 2020-11-08 04:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0015_auto_20201108_0423'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionDelivery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('delivery_status', models.IntegerField()),
                ('delivery_location_name', models.CharField(max_length=200)),
                ('delivery_aqi', models.IntegerField()),
                ('delivery_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscriptions.User')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='SubscriptionMessages',
        ),
    ]
