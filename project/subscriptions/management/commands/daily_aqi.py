from datetime import timedelta, time, datetime

from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.timezone import make_aware
from subscriptions.models import UserSubscription

today = timezone.now()
tomorrow = today + timedelta(1)
today_start = make_aware(datetime.combine(today, time()))
today_end = make_aware(datetime.combine(tomorrow, time()))


class Command(BaseCommand):
    help = "Send Today's AQI to subscribers"

    def handle(self, *args, **options):
        user_subs = UserSubscription.objects.all()
        if user_subs:
            message = ""

            for user_sub in user_subs:
                message += f"{user_sub} \n"

            self.stdout.write("AQI report was sent was sent.")
        else:
            self.stdout.write("No subscribers to sent")
