from django.db import models

GENDER_CHOICES = (
    (0, 'male'),
    (1, 'female'),
    (2, 'not specified'),
    (9, 'non binary'),
)

DELIVERY_FREQ = (
    (1, 'Once a day'),
    (2, 'Twice a day'),
)


# Create your models here.
class SubscriptionType(models.Model):
    name = models.CharField(max_length=200)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    message = models.CharField(max_length=200)
    send_only_to_subscribers = models.BooleanField()

    def __str__(self):
        return self.message


class Subscription(models.Model):
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class User(models.Model):
    class Meta:
        unique_together = (('platform', 'platform_id'),)

    platform = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200)
    platform_id = models.CharField(max_length=200, null=True)
    dob = models.IntegerField(null=True)
    gender = models.IntegerField(choices=GENDER_CHOICES,
                                 default=2)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class UserSubscription(models.Model):
    subscription_user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    delivery_frequency = models.IntegerField(choices=DELIVERY_FREQ,
                                             default=1)

    subscription_location_name = models.CharField(max_length=200)
    subscription_location_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    subscription_location_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_archived = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subscription_user.full_name


class Recommendation(models.Model):
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    recommendation_category = models.CharField(max_length=200)
    recommendation = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.recommendation


class AQIRequestLog(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.full_name


class Program(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    content_url = models.URLField()
    reveal_day = models.IntegerField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
