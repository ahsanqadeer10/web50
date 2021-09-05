from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("listing/create", views.create, name="create"),
    path("listing/<int:listing_id>/watch", views.watch, name="watch"),
    path("listing/<int:listing_id>/unwatch", views.unwatch, name="unwatch"),
    path("listing/<int:listing_id>/bid", views.bid, name="bid"),
    path("listing/<int:listing_id>/close", views.close, name="close")
]
