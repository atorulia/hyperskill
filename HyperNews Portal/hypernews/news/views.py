from django.shortcuts import render, HttpResponse
import json

from django.conf import settings

with open(settings.NEWS_JSON_PATH, 'r') as json_file:
    articles = json.load(json_file)


def home(request):
    return HttpResponse('Coming soon')


def post_detail_view(request, article_link):
    # if len(article_link) == 0:
    #     return render(request, 'news/base.html')

    for article in articles:
        if article['link'] == int(article_link):
            print({"article": article})
            return render(request, 'news/main.html', {"article": article})
