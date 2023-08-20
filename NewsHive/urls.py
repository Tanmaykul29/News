from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("news", views.news, name="news"),
    path('news/save-to-favorites/<str:title_slug>/', views.save_to_favorites, name='save_to_favorites'),
    path('favorites', views.favorites, name='favorites'),
    path('remove_favorite/<int:favorite_id>/', views.remove_from_favorites, name='remove_favorite'),

    path('add_comment/', views.add_comment, name='add_comment'),
    path('edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]
