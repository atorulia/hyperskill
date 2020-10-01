from django.shortcuts import render, redirect
from . import models
from django.views import View
from .forms import *
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User

class VacanciesView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "vacancies/vacancies.html", context={'Vacancies': models.Vacancy.objects.all()})


class CreateVacancyView(View):
    def get(self, request):
        form = CreateVacancyForm()
        return render(request, "vacancies/create_vacancy.html", context={'form': form})

    def post(self, request):
        form = CreateVacancyForm(request.POST)
        if form.is_valid():
            if request.user.is_staff:
                models.Vacancy.objects.create(description=request.POST.get("description"), author=request.user)
                print(request.POST)
            else:
                return HttpResponseForbidden()
            return redirect('/home')
        else:
            return HttpResponseForbidden()