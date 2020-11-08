from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Recommendation, AQIRequestLog, FollowUpQuestions, Subscription, User, UserSubscription, \
    SubscriptionDelivery


@admin.register(SubscriptionDelivery)
class SubscriptionDeliveryAdmin(ImportExportModelAdmin):
    list_display = ('id','delivery_user', 'delivery_status', 'created', 'updated')

    pass


@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    pass


@admin.register(UserSubscription)
class UserSubscriptionAdmin(ImportExportModelAdmin):
    pass


@admin.register(FollowUpQuestions)
class FollowUpQuestionsAdmin(ImportExportModelAdmin):
    pass


@admin.register(Recommendation)
class RecommendationAdmin(ImportExportModelAdmin):
    pass


@admin.register(AQIRequestLog)
class AQIRequestLogAdmin(ImportExportModelAdmin):
    pass


@admin.register(Subscription)
class SubscriptionAdmin(ImportExportModelAdmin):
    pass
