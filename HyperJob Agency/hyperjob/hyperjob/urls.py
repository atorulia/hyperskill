from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from .views import *
from resume.views import *
from vacancy.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainView.as_view()),
    path('resumes', ResumesView.as_view()),
    path('vacancies', VacanciesView.as_view()),
    path('resume/new', CreateResumeView.as_view()),
    path('vacancy/new', CreateVacancyView.as_view()),
    path('login', LoginView.as_view()),
    path('signup', SignUpView.as_view()),
    path('login/', RedirectView.as_view(url='/login')),
    path('signup/', RedirectView.as_view(url='/signup')),
    path('home', ProfileView.as_view()),
]