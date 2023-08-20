import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import User, FavoriteNews, Comment
import requests
from .forms import CommentForm, EditCommentForm
from slugify import slugify


def index(request):
    comments = Comment.objects.all()
    return render(request, "index.html", {"comments": comments})


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


@login_required()
def save_to_favorites(request, title_slug):
    if request.user.is_authenticated:
        for article in global_articles:
            tp = article['title']
            if tp == title_slug:
                fnews = FavoriteNews()
                fnews.title = article['title']
                fnews.description = article['description']
                fnews.image_url = article['urlToImage']
                fnews.article_url = article['url']
                fnews.user = request.user
                fnews.save()

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


@login_required
def add_comment(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.save()
            return redirect("index")
    else:
        form = CommentForm()
    return render(request, "index.html", {"form": form})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, user=request.user)
    if comment.user == request.user:
        comment.delete()
    return redirect('index')


@login_required()
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.method == "POST":
        form = EditCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = EditCommentForm(instance=comment)

    return render(request, "edit_comment.html", {"form": form, "comment": comment})

# python3 manage.py makemigrations NewsHive
# python3 manage.py migrate
# python3 manage.py runserver


