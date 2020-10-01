from django.views import View
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from collections import deque


active_client_identifier = ''


class WelcomeView(View):
    @staticmethod
    def get(request):
        return HttpResponse('Welcome to the Hypercar Service!')


class MenuView(View):
    choices = {
        "change_oil": "Change oil",
        "inflate_tires": "Inflate tires",
        "diagnostic": "Get diagnostic test",
    }

    def get(self, request):
        return render(request, 'tickets/menu.html', context={"choices": self.choices})


class TicketView(View):
    change_oil_queue = deque()
    inflate_tires_queue = deque()
    diagnostics_queue = deque()
    line_of_cars = {"change_oil": change_oil_queue,
                    "inflate_tires": inflate_tires_queue,
                    "diagnostic": diagnostics_queue,
                    }
    waiting_time = {"change_oil": 2,
                    "inflate_tires": 5,
                    "diagnostic": 30,
                    }

    def get(self, request, service):
        user_id = len(self.change_oil_queue) + len(self.inflate_tires_queue) + len(self.diagnostics_queue) + 1
        time = 0
        for key in self.line_of_cars.keys():
            time += len(self.line_of_cars[key]) * self.waiting_time[key]
            if service == key:
                self.line_of_cars[key].append(user_id)
                break
        context = {"title": service,
                   "ticket_number": user_id,
                   "estimated_time": time}

        return render(request, 'tickets/get_ticket.html', context=context)


class ProcessingView(View):
    @staticmethod
    def get(request):
        queue_lens = {"change_oil": len(TicketView.line_of_cars['change_oil']),
                      "inflate_tires": len(TicketView.line_of_cars['inflate_tires']),
                      "diagnostic": len(TicketView.line_of_cars['diagnostic'])}
        return render(request, "tickets/processing.html", {"queue": queue_lens})

    @staticmethod
    def post(request):
        for action in TicketView.line_of_cars:
            if TicketView.line_of_cars[action]:
                global active_client_identifier
                active_client_identifier = TicketView.line_of_cars[action].popleft()
                break
            active_client_identifier = ''
        return HttpResponseRedirect('/next')


class NextView(View):
    @staticmethod
    def get(request):
        return render(request, "tickets/next.html", {"active_client": active_client_identifier})
