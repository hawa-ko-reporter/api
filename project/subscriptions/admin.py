from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Recommendation, AQIRequestLog


@admin.register(Recommendation)
class RecommendationAdmin(ImportExportModelAdmin):
    pass


@admin.register(AQIRequestLog)
class AQIRequestLogAdmin(ImportExportModelAdmin):
    pass
