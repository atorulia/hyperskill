from django.urls import path, re_path
from tickets.views import *
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='welcome/', permanent=False)),
    path('welcome/', WelcomeView.as_view(), name="welcome"),
    path('menu/', MenuView.as_view(), name="menu"),
    path('get_ticket/<service>', TicketView.as_view(), name="tickets"),
    path('processing', ProcessingView.as_view(), name="processing"),
    path('processing/', RedirectView.as_view(url='/processing')),
    path('next', NextView.as_view(), name="next")
]
