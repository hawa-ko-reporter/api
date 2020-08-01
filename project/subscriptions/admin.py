from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Recommendation


@admin.register(Recommendation)
class PersonAdmin(ImportExportModelAdmin):
    pass
