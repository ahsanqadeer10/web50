
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("post/<int:post_id>/edit", views.post_edit, name="post_edit"),
    path("post/<int:post_id>/like", views.post_like, name="post_like"),
    path("post/<int:post_id>/unlike", views.post_unlike, name="post_unlike" ),
    path("post/<int:post_id>/delete", views.post_delete, name="post_delete"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("profile/<str:username>/follow_toggle", views.follow_toggle, name="follow_toggle"),
    path("following", views.following, name="following")
]
