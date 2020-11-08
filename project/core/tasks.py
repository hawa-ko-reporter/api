from celery import shared_task
from django.core.management import call_command


@shared_task
def sample_task():
    print("The daily aqi task just ran.")
    call_command("aqi_subscriptions_response", )


@shared_task
def send_email_report():
    print("The report task just ran.")
    # call_command("daily_aqi", )




@shared_task
def send_daily_message():
    print("The daily message task just ran.")
    # call_command("daily_message", )

