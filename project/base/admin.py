from django.contrib import admin
from .models import Vacancy


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('name', 'salary_from', 'salary_to', 'area_name', 'published_at')
    search_fields = ('name', 'key_skills')
