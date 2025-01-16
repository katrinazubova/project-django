import csv
from datetime import datetime
from collections import defaultdict

def process_csv(file_path):
    vacancies = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            vacancy = {
                'title': row['title'],
                'salary_from': float(row['salary_from']) if row['salary_from'] else None,
                'salary_to': float(row['salary_to']) if row['salary_to'] else None,
                'currency': row['currency'],
                'city': row['city'],
                'published_at': datetime.strptime(row['published_at'], '%Y-%m-%d'),
                'key_skills': row['key_skills'].split(', ') if row['key_skills'] else [],
            }
            if vacancy['salary_from'] and vacancy['salary_to'] and vacancy['salary_from'] <= 10_000_000 and vacancy['salary_to'] <= 10_000_000:
                vacancies.append(vacancy)
    return vacancies