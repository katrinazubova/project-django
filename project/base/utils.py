import csv
from django.contrib import messages
from io import TextIOWrapper

from .models import Vacancy_csv


def import_csv_to_db(modeladmin, request, queryset):
    file = request.FILES.get('csv_file')
    if not file:
        messages.error(request, "Вы должны выбрать CSV-файл для загрузки.")
        return

    try:
        csv_data = csv.reader(TextIOWrapper(file, encoding='utf-8'))
        next(csv_data)
        for row in csv_data:
            Vacancy_csv.objects.create(
                name=row[0],
                description=row[1],
                key_skills=row[2],
                salary_from=row[3] or None,
                salary_to=row[4] or None,
                published_at=row[5],
            )
        messages.success(request, "Данные успешно импортированы!")
    except Exception as e:
        messages.error(request, f"Ошибка при обработке файла: {e}")