from django.contrib import admin
from .models import Vacancy
from .models import Statistics
from .models import Vacancy_csv
from .utils import import_csv_to_db

admin.site.register(Vacancy)
admin.site.register(Statistics)
admin.site.register(Vacancy_csv)


class VacancyAdmin(admin.ModelAdmin):
    list_display = ('name', 'salary_from', 'salary_to', 'published_at')
    actions = [import_csv_to_db]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'import_csv_to_db' in actions:
            actions['import_csv_to_db'] = (
                actions['import_csv_to_db'][0],
                actions['import_csv_to_db'][1],
                "Импортировать CSV",
            )
        return actions

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_import_form'] = True
        return super().changelist_view(request, extra_context=extra_context)