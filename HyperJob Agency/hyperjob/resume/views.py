from django.shortcuts import render, redirect
from . import models
from django.views import View
from .forms import *
from django.http import HttpResponseForbidden


class ResumesView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "resumes/resumes.html", context={'Resumes': models.Resume.objects.all()})


class CreateResumeView(View):
    def get(self, request):
        form = CreateResumeForm()
        return render(request, "resumes/create_resume.html", context={'form': form})

    def post(self, request):
        form = CreateResumeForm(request.POST)
        if form.is_valid():
            if not request.user.is_staff:
                models.Resume.objects.create(description=request.POST.get("description"), author=request.user)
                return redirect('/home')
            else:
                return HttpResponseForbidden()
        else:
            return HttpResponseForbidden()

