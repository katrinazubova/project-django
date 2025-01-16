from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.index, name="index"),
    path('about/', views.statistics_view, name='about'),
 ]