from django.shortcuts import render, HttpResponse, redirect
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User


class MainView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "main/main.html")


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = 'login'
    template_name = 'signup/signup.html'


class LoginView(LoginView):
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    template_name = 'login/login.html'


class ProfileView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'profile/profile.html', context={'is_staff':request.user.is_staff})
        # if request.user.is_authenticated:
        #     if User.is_staff:
        #         return redirect('/vacancy/new')
        #     else:
        #         return redirect('/resume/new')
        # else:
        #     return redirect('/home')
