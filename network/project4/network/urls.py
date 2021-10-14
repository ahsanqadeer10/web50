
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("post/<int:post_id>/edit", views.post_edit, name="post_edit"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("profile/<str:username>/follow_toggle", views.follow_toggle, name="follow_toggle"),
    path("following", views.following, name="following")
]
