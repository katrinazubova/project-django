import csv
from datetime import datetime
import requests
from collections import Counter
from django.db.models import Avg, Count

EXCHANGE_RATE_API = "https://www.cbr.ru/scripts/XML_daily.asp"


def get_exchange_rate(currency, date):
    try:
        response = requests.get(f"{EXCHANGE_RATE_API}?date_req={date.strftime('%d/%m/%Y')}")
        if response.status_code == 200:
            xml = response.text
            start = xml.find(f"<CharCode>{currency.upper()}</CharCode>")
            if start != -1:
                value_start = xml.find("<Value>", start) + len("<Value>")
                value_end = xml.find("</Value>", start)
                return float(xml[value_start:value_end].replace(',', '.'))
    except Exception as e:
        print(f"Error fetching exchange rate for {currency} on {date}: {e}")
    return 1  # Default to 1 if no conversion available


def process_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                salary_from = float(row['salary_from']) if row['salary_from'] else 0
                salary_to = float(row['salary_to']) if row['salary_to'] else 0
                salary_avg = (salary_from + salary_to) / 2 if salary_from and salary_to else salary_from or salary_to

                if salary_avg > 10_000_000:  # Skip outliers
                    continue

                published_date = datetime.strptime(row['published_at'], '%Y-%m-%d')
                currency = row['salary_currency']

                if currency != "RUR" and currency:  # Convert to RUB
                    exchange_rate = get_exchange_rate(currency, published_date)
                    salary_avg *= exchange_rate

                Vacancy.objects.create(
                    name=row['name'],
                    description=row['description'],
                    key_skills=row['key_skills'],
                    experience_id=row['experience_id'],
                    premium=row['premium'] == 'True',
                    employer_name=row['employer_name'],
                    salary_from=salary_from,
                    salary_to=salary_to,
                    salary_currency=row['salary_currency'],
                    area_name=row['area_name'],
                    published_at=published_date
                )
            except Exception as e:
                print(f"Error processing row: {e}")


def calculate_statistics():
    data = {
        "salary_by_year": Vacancy.objects.values('published_at__year')
        .annotate(avg_salary=Avg('salary_from'))
        .order_by('published_at__year'),
        "vacancy_count_by_year": Vacancy.objects.values('published_at__year')
        .annotate(count=Count('id'))
        .order_by('published_at__year'),
        "salary_by_city": Vacancy.objects.values('area_name')
        .annotate(avg_salary=Avg('salary_from'))
        .order_by('-avg_salary'),
        "vacancy_share_by_city": Vacancy.objects.values('area_name')
        .annotate(count=Count('id'))
        .order_by('-count'),
        "top_skills_by_year": {}
    }

    for year in Vacancy.objects.dates('published_at', 'year'):
        skills = Counter()
        for vacancy in Vacancy.objects.filter(published_at__year=year.year):
            if vacancy.key_skills:
                skills.update(vacancy.key_skills.split(', '))
        data["top_skills_by_year"][year.year] = skills.most_common(20)

    return data
