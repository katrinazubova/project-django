from django.contrib.sites import requests
from django.http import JsonResponse
from django.shortcuts import render


def layout(request):
    return render(request, 'frontend/layout.html')
def index(request):
    return render(request, 'frontend/index.html')
def about(request):
    return render(request, 'frontend/about.html')

def get_all_currency(ET=None):
    month = 1
    year = 2020
    all_currency = 'BYR,USD,EUR,KZT,UAH,AZN,KGS,UZS,GEL'.split(',')
    result = {}

    while True:
        if year == 2024 and month == 12:
            break
        month_str = f"{month:02d}"
        try:
            response = requests.get(f'https://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{month_str}/{year}')
            if response.status_code != 200:
                continue

            root = ET.fromstring(response.content)
            result[f'{year}-{month_str}'] = {}

            for item in root.findall('Valute'):
                name = item.find('CharCode').text
                if name in all_currency:
                    value = float(item.find('Value').text.replace(',', '.'))
                    result[f'{year}-{month_str}'][name] = value

        except Exception as e:
            print(f"Ошибка обработки данных: {e}")
            continue

        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

    return result


def statistics_view(request):
    try:
        stats = get_all_currency()

        # Средние зарплаты по годам
        salary_by_year = {
            year: sum(values.values()) / len(values)
            for year, values in stats.items() if values
        }

        # Пример данных для количества вакансий по годам (заполните реальными данными при их наличии)
        vacancy_count_by_year = {
            year: len(values)
            for year, values in stats.items() if values
        }

        # Средние зарплаты по городам
        city_salary_data = {}  # Сначала собираем данные по городам
        for year, values in stats.items():
            for city, salary in values.items():
                city_salary_data.setdefault(city, []).append(salary)

        salary_by_city = {
            city: sum(salaries) / len(salaries)
            for city, salaries in city_salary_data.items() if salaries
        }

        # Доли вакансий по городам
        total_vacancies = sum(len(v) for v in city_salary_data.values())
        vacancy_share_by_city = {
            city: (len(salaries) / total_vacancies) * 100
            for city, salaries in city_salary_data.items() if total_vacancies > 0
        }

        # ТОП-20 навыков (пример заглушки, заменить на актуальные данные)
        top_skills = [
            ("Skill A", 150),
            ("Skill B", 120),
            ("Skill C", 100),
        ]

        data = {
            'salary_by_year': salary_by_year,
            'vacancy_count_by_year': vacancy_count_by_year,
            'salary_by_city': salary_by_city,
            'vacancy_share_by_city': vacancy_share_by_city,
            'top_skills': top_skills
        }

        return render(request, 'baza/general_stat.html', {'stats': data})

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=500)

