from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Recommendation, AQIRecommendations, FollowUpQuestions,Subscription


@admin.register(FollowUpQuestions)
class FollowUpQuestionsAdmin(ImportExportModelAdmin):
    pass

@admin.register(Recommendation)
class RecommendationAdmin(ImportExportModelAdmin):
    pass

@admin.register(AQIRecommendations)
class AQIRequestLogAdmin(ImportExportModelAdmin):
    pass

@admin.register(Subscription)
class SubscriptionAdmin(ImportExportModelAdmin):
    pass
