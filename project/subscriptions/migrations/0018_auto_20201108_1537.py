# Generated by Django 3.0.5 on 2020-11-08 15:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0017_subscriptiondelivery_delivery_status_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='AQIRequestLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('location_name', models.CharField(max_length=200, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscriptions.User')),
            ],
        ),
        migrations.DeleteModel(
            name='AQIRecommendations',
        ),
    ]
