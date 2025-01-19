from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect


def layout(request):
    return render(request, 'frontend/layout.html')
def index(request):
    return render(request, 'frontend/index.html')



