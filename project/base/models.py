from django.db import models

class Vacancy(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    salary_from = models.FloatField(null=True, blank=True, verbose_name="Минимальная зарплата")
    salary_to = models.FloatField(null=True, blank=True, verbose_name="Максимальная зарплата")
    currency = models.CharField(max_length=10, verbose_name="Валюта")
    published_date = models.DateField(verbose_name="Дата публикации")
    city = models.CharField(max_length=255, verbose_name="Город")
    key_skills = models.TextField(null=True, blank=True, verbose_name="Навыки")

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'

class Statistics(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    html_content = models.TextField(verbose_name="HTML-контент")
    graph_image = models.ImageField(upload_to="graphs/", verbose_name="График", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'


class Vacancy_csv(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    key_skills = models.TextField()
    salary_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    published_at = models.DateField()

    def __str__(self):
        return self.name