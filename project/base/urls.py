from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('stats/', views.statistics_view, name='stats'),
    path('demand/', views.demand_view, name='demand'),
    path('geography/', views.geography_view, name='geography'),
    path('skills/', views.skills_view, name='skills'),
    path('last_vac/', views.last_vac_view, name='last_vac'),
 ]