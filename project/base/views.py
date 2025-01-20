from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.sites import requests
from django.db.models import Q
from django.shortcuts import redirect
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.shortcuts import render
from collections import defaultdict
from .models import Vacancy
import requests


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'base/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'base/login.html', {'form': form})

def profile(request):
    return render(request, 'profile.html', {'user': request.user})

def get_currency_rate(currency, date):
    if currency == 'RUB':
        return 1.0

    formatted_date = date.strftime('%d/%m/%Y')
    url = f"{formatted_date}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text

        if f"<CharCode>{currency}</CharCode>" in data:
            start = data.find(f"<CharCode>{currency}</CharCode>")
            value_start = data.find("<Value>", start) + len("<Value>")
            value_end = data.find("</Value>", value_start)
            rate = data[value_start:value_end].replace(',', '.')
            return float(rate)

        return None
    except Exception as e:
        print(f"Ошибка при получении курса валюты: {e}")
        return None

def statistics_view(request):
    try:
        currency_rates_cache = {}

        def get_cached_currency_rate(currency, date):
            if currency == 'RUB':
                return 1.0
            key = (currency, date.year, date.month)
            if key not in currency_rates_cache:
                rate = get_currency_rate(currency, datetime(date.year, date.month, 1))
                currency_rates_cache[key] = rate or 1.0
            return currency_rates_cache[key]

        prioritized_cities = [
            "Москва", "Санкт-Петербург", "Екатеринбург", "Новосибирск", "Казань",
            "Минск", "Краснодар", "Нижний Новгород", "Алматы", "Ростов-на-Дону",
            "Воронеж", "Самара", "", "", "", "", "", "", "", ""
        ]

        valid_vacancies = Vacancy.objects.exclude(salary_from__gt=10000000, salary_to__gt=10000000)

        salary_by_year = defaultdict(float)
        vacancy_count_by_year = defaultdict(int)
        salary_by_city = defaultdict(list)
        total_vacancies = valid_vacancies.count()

        for vacancy in valid_vacancies:
            salary_from = vacancy.salary_from or 0
            salary_to = vacancy.salary_to or 0
            if salary_from == 0 and salary_to == 0:
                continue

            avg_salary = (salary_from + salary_to) / 2
            rate = get_cached_currency_rate(vacancy.salary_currency, vacancy.published_at)
            salary_in_rub = avg_salary * rate

            year = vacancy.published_at.year
            salary_by_year[year] += salary_in_rub
            vacancy_count_by_year[year] += 1

            city = vacancy.area_name.strip() if vacancy.area_name else "Не указано"
            salary_by_city[city].append(salary_in_rub)

        salary_by_year_avg = sorted(
            [
                {'year': year, 'avg_salary': total / vacancy_count_by_year[year]}
                for year, total in salary_by_year.items()
            ],
            key=lambda x: x['year']
        )

        salary_by_city_avg = sorted(
            [
                {'city': city, 'avg_salary': sum(salaries) / len(salaries)}
                for city, salaries in salary_by_city.items() if city != "Не указано"
            ],
            key=lambda x: (prioritized_cities.index(x['city']) if x['city'] in prioritized_cities else float('inf'),
                           -x['avg_salary'])
        )

        vacancy_share_by_city = sorted(
            [
                {'city': city, 'vacancy_share': (len(salaries) / total_vacancies) * 100}
                for city, salaries in salary_by_city.items() if city != "Не указано"
            ],
            key=lambda x: (prioritized_cities.index(x['city']) if x['city'] in prioritized_cities else float('inf'),
                           -x['vacancy_share'])
        )

        top_skills_data = valid_vacancies.values_list('key_skills', flat=True)
        skills_frequency = defaultdict(int)
        for skills in top_skills_data:
            if skills:
                for skill in skills.split(','):
                    skills_frequency[skill.strip()] += 1
        top_skills = sorted(skills_frequency.items(), key=lambda x: x[1], reverse=True)[:20]

        vacancy_count_by_year_avg = sorted(
            [
                {'year': year, 'vacancy_count': count}
                for year, count in vacancy_count_by_year.items()
            ],
            key=lambda x: x['year']
        )

        data = {
            'salary_by_year': salary_by_year_avg,
            'vacancy_count_by_year': vacancy_count_by_year_avg,
            'salary_by_city': salary_by_city_avg,
            'vacancy_share_by_city': vacancy_share_by_city,
            'top_skills': top_skills,
        }

        return render(request, 'base/stats.html', {'stats': data, 'title': 'Общая статистика'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def demand_view(request):
    try:
        currency_rates_cache = {}

        def get_cached_currency_rate(currency, date):
            if currency == 'RUB':
                return 1.0
            key = (currency, date.year, date.month)
            if key not in currency_rates_cache:
                rate = get_currency_rate(currency, datetime(date.year, date.month, 1))
                currency_rates_cache[key] = rate or 1.0
            return currency_rates_cache[key]

        frontend_keywords = [
            'frontend', 'фронтенд', 'вёрстка', 'верстка', 'верста',
            'front end', 'angular', 'html', 'css', 'react', 'vue'
        ]

        valid_vacancies = Vacancy.objects.exclude(salary_from__gt=10000000, salary_to__gt=10000000)
        filter_condition = Q()
        for keyword in frontend_keywords:
            filter_condition |= Q(key_skills__icontains=keyword)

        filtered_vacancies = valid_vacancies.filter(filter_condition)

        salary_by_year = defaultdict(float)
        vacancy_count_by_year = defaultdict(int)
        salary_by_city = defaultdict(list)
        total_vacancies = filtered_vacancies.count()

        for vacancy in filtered_vacancies:
            salary_from = vacancy.salary_from or 0
            salary_to = vacancy.salary_to or 0
            if salary_from == 0 and salary_to == 0:
                continue

            avg_salary = (salary_from + salary_to) / 2
            rate = get_cached_currency_rate(vacancy.salary_currency, vacancy.published_at)
            salary_in_rub = avg_salary * rate

            year = vacancy.published_at.year
            salary_by_year[year] += salary_in_rub
            vacancy_count_by_year[year] += 1

            city = vacancy.area_name.strip() if vacancy.area_name else "Не указано"
            salary_by_city[city].append(salary_in_rub)

        salary_by_year_avg = [
            {'year': year, 'avg_salary': total / vacancy_count_by_year[year]}
            for year, total in salary_by_year.items()
        ]

        salary_by_city_avg = sorted(
            [
                {'city': city, 'avg_salary': sum(salaries) / len(salaries)}
                for city, salaries in salary_by_city.items() if city != "Не указано"
            ],
            key=lambda x: -x['avg_salary']
        )

        vacancy_share_by_city = sorted(
            [
                {'city': city, 'vacancy_share': (len(salaries) / total_vacancies) * 100}
                for city, salaries in salary_by_city.items() if city != "Не указано"
            ],
            key=lambda x: -x['vacancy_share']
        )

        top_skills_data = filtered_vacancies.values_list('key_skills', flat=True)
        skills_frequency = defaultdict(int)
        for skills in top_skills_data:
            if skills:
                for skill in skills.split(','):
                    skills_frequency[skill.strip()] += 1
        top_skills = sorted(skills_frequency.items(), key=lambda x: x[1], reverse=True)[:20]

        data = {
            'salary_by_year': salary_by_year_avg,
            'vacancy_count_by_year': [
                {'year': year, 'vacancy_count': count}
                for year, count in vacancy_count_by_year.items()
            ],
            'salary_by_city': salary_by_city_avg,
            'vacancy_share_by_city': vacancy_share_by_city,
            'top_skills': top_skills,
        }

        return render(request, 'base/demand.html', {'stats': data, 'title': 'Востребованность'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def geography_view(request):
    try:
        currency_rates_cache = {}

        def get_cached_currency_rate(currency, date):
            if currency == 'RUB':
                return 1.0
            key = (currency, date.year, date.month)
            if key not in currency_rates_cache:
                rate = get_currency_rate(currency, datetime(date.year, date.month, 1))
                currency_rates_cache[key] = rate or 1.0
            return currency_rates_cache[key]

        profession_keywords = ['frontend', 'фронтенд', 'вёрстка', 'верстка', 'верста', 'front end', 'angular', 'html',
                               'css', 'react', 'vue']

        query = Q()
        for keyword in profession_keywords:
            query |= Q(key_skills__icontains=keyword)

        valid_vacancies = Vacancy.objects.filter(query).exclude(salary_from__gt=10000000, salary_to__gt=10000000)

        salary_by_city = defaultdict(list)
        vacancy_count_by_city = defaultdict(int)
        total_vacancies = valid_vacancies.count()

        for vacancy in valid_vacancies:
            salary_from = vacancy.salary_from or 0
            salary_to = vacancy.salary_to or 0
            if salary_from == 0 and salary_to == 0:
                continue

            avg_salary = (salary_from + salary_to) / 2
            rate = get_cached_currency_rate(vacancy.salary_currency, vacancy.published_at)
            salary_in_rub = avg_salary * rate

            city = vacancy.area_name.strip() if vacancy.area_name else "Не указано"
            salary_by_city[city].append(salary_in_rub)
            vacancy_count_by_city[city] += 1

        salary_by_city_avg = [
            {'city': city, 'avg_salary': sum(salaries) / len(salaries)}
            for city, salaries in salary_by_city.items() if city != "Не указано"
        ]

        salary_by_city_avg = sorted(salary_by_city_avg, key=lambda x: x['avg_salary'], reverse=True)

        vacancy_share_by_city = [
            {'city': city, 'vacancy_share': (vacancy_count_by_city[city] / total_vacancies) * 100}
            for city in salary_by_city if city != "Не указано"
        ]

        vacancy_share_by_city = sorted(vacancy_share_by_city, key=lambda x: x['vacancy_share'], reverse=True)

        data = {
            'salary_by_city': salary_by_city_avg,
            'vacancy_share_by_city': vacancy_share_by_city,
        }

        return render(request, 'base/geography.html', {'stats': data, 'title': 'География'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def skills_view(request):
    try:
        currency_rates_cache = {}

        def get_cached_currency_rate(currency, date):
            if currency == 'RUB':
                return 1.0
            key = (currency, date.year, date.month)
            if key not in currency_rates_cache:
                rate = get_currency_rate(currency, datetime(date.year, date.month, 1))
                currency_rates_cache[key] = rate or 1.0
            return currency_rates_cache[key]

        profession_keywords = ['frontend', 'фронтенд', 'вёрстка', 'верстка', 'верста', 'front end', 'angular', 'html',
                               'css', 'react', 'vue']

        query = Q()
        for keyword in profession_keywords:
            query |= Q(key_skills__icontains=keyword)

        valid_vacancies = Vacancy.objects.filter(query).exclude(salary_from__gt=10000000, salary_to__gt=10000000)

        top_skills_data = valid_vacancies.values_list('key_skills', flat=True)
        skills_frequency = defaultdict(int)
        for skills in top_skills_data:
            if skills:
                for skill in skills.split(','):
                    skills_frequency[skill.strip()] += 1
        top_skills = sorted(skills_frequency.items(), key=lambda x: x[1], reverse=True)[:20]

        data = {
            'top_skills': top_skills,
        }

        return render(request, 'base/skills.html', {'stats': data, 'title': 'Навыки'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




BASE_URL = "https://api.hh.ru/vacancies"
SEARCH_TEXT = "Frontend-программист"
DATE_FROM = (datetime.now() - timedelta(days=1)).isoformat()
DATE_TO = datetime.now().isoformat()
HEADERS = {"User-Agent": "YourDjangoApp/1.0"}


def fetch_vacancies():
    params = {
        "text": SEARCH_TEXT,
        "date_from": DATE_FROM,
        "date_to": DATE_TO,
        "per_page": 10,
        "order_by": "publication_time",
        "only_with_salary": False,
    }
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json().get("items", [])


def fetch_vacancy_details(vacancy_id):
    url = f"{BASE_URL}/{vacancy_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    details = response.json()
    return {
        "description": details.get("description", ""),
        "skills": ", ".join(skill["name"] for skill in details.get("key_skills", [])),
    }


def last_vac_view(request):
    try:
        vacancies = fetch_vacancies()
        results = []
        for vacancy in vacancies:
            details = fetch_vacancy_details(vacancy["id"])
            results.append({
                "title": vacancy["name"],
                "description": details["description"],
                "skills": details["skills"],
                "company": vacancy["employer"]["name"],
                "salary": format_salary(vacancy["salary"]),
                "region": vacancy["area"]["name"],
                "published_at": vacancy["published_at"],
            })
    except Exception as e:
        results = []
        print(f"Ошибка при получении данных: {e}")

    return render(request, 'base/last_vac.html', {"vacancies": results})


def format_salary(salary):
    if not salary:
        return "Не указана"
    salary_from = salary.get("from")
    salary_to = salary.get("to")
    currency = salary.get("currency", "")
    if salary_from and salary_to:
        return f"{salary_from} - {salary_to} {currency}"
    elif salary_from:
        return f"От {salary_from} {currency}"
    elif salary_to:
        return f"До {salary_to} {currency}"
    return "Не указана"



