from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import User, FavoriteNews
import requests
from slugify import slugify

def index(request):
    return render(request, "index.html")


NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
API_KEY = "c8012026421644c983aa9c308859c304"

global_articles = []
@login_required()
def news(request):
    global global_articles
    category = request.GET.get('category', 'general')  # Default to 'general' if no category is provided in the URL

    params = {
        'country': 'in',
        'category': category,
        'apiKey': API_KEY,
    }

    response = requests.get(NEWS_API_URL, params=params)

    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get('articles', [])
        global_articles = articles
    else:
        articles = []

    return render(request, 'news.html', {'articles': articles, 'category': category})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":

        email = request.POST["email"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(email, email, password)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "register.html")


# def get_article_by_title(title):
#     # Loop through the list of articles to find the one with a matching title
#     for article in Global_articles:
#         if article['title'] == title:
#             return article
#
#     # If no matching article is found, return None or handle accordingly
#     return None


# def save_to_favorites(request, title_slug):
#     if request.user.is_authenticated:
#         title = title_slug.replace('-', ' ')  # Convert the slug back to the original title
#         article = get_article_by_title(title)  # Implement this function to fetch the article by title
#         if article:
#             FavoriteNews.objects.create(
#                 user=request.user,
#                 title=article['title'],
#                 description=article['description'],
#                 image_url=article['urlToImage'],
#                 article_url=article['url'],
#             )
#             print(f"\n\nThe saved news is: title: {{title}}\n\n")
#     return redirect('news')  # Redirect to the news list page

@login_required()
def save_to_favorites(request, title_slug):
    if request.user.is_authenticated:
        # title = title_slug.replace('-', ' ')  # Convert the slug back to the original title
        # article = get_article_by_title(title_slug)  # Implement this function to fetch the article by title

        for article in global_articles:
            tp = article['title']
            txt = slugify(tp)
            if txt == title_slug:
                fnews = FavoriteNews()
                fnews.title = article['title']
                fnews.description = article['description']
                fnews.image_url = article['urlToImage']
                fnews.article_url = article['url']
                fnews.user = request.user
                fnews.save()

        # if article:
        #     fnews = FavoriteNews()
        #     fnews.title = article['title']
        #     fnews.description = article['description']
        #     fnews.image_url = article['urlToImage']
        #     fnews.article_url = article['url']
        #     fnews.user = request.user
        #     fnews.save()
        #     return HttpResponseRedirect(reverse('favorites'))
        # return render(request, 'favorites.html', {'article': article, 'title': title_slug, 'global_articles':global_articles})

    return redirect('news')  # Redirect to the news list page

@login_required()
def favorites(request):

    if request.user.is_authenticated:
        favorite_news = FavoriteNews.objects.filter(user=request.user)
    else:
        favorite_news = []

    return render(request, 'favorites.html', {'favorite_news': favorite_news})


@login_required()
def remove_from_favorites(request, favorite_id):
    favorite_article = get_object_or_404(FavoriteNews, id=favorite_id, user=request.user)

    # Check if the user owns the favorite article
    if favorite_article.user == request.user:
        favorite_article.delete()

    return redirect('favorites')


# python manage.py makemigrations NewsHive
# python3 manage.py migrate
# python3 manage.py runserver


