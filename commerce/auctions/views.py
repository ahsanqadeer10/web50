from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Category, Bid


def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url='/login')
def create(request):
    if request.method == "POST":

        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = int(request.POST["starting_bid"])
        image = request.POST["image"]
        category = Category.objects.get(pk=int(request.POST["category"]))

        listing = Listing(title=title, description=description, starting_bid=starting_bid,
                          image=image, category=category, creator=request.user)
        listing.save()
        return HttpResponseRedirect(reverse('index'))

    categories = Category.objects.all()
    return render(request, "auctions/create.html", {
        "categories": categories
    })


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user_watchlist = None
    if request.user.is_authenticated:
        user_watchlist = request.user.watchlist.all()
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "user_watchlist": user_watchlist
    })


@login_required(login_url='/login')
def watch(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    request.user.watchlist.add(listing)
    return HttpResponseRedirect(reverse('listing', args=(listing_id, )))


@login_required(login_url='/login')
def unwatch(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    request.user.watchlist.remove(listing)
    return HttpResponseRedirect(reverse('listing', args=(listing_id, )))


@login_required(login_url='/login')
def bid(request, listing_id):
    if request.method == "POST":
        value = int(request.POST["value"])
        listing = Listing.objects.get(pk=listing_id)
        if value <= listing.starting_bid or value <= listing.highest_bid:
            return render(request, 'auctions/listing.html', {
                "listing": listing,
                "user_watchlist": request.user.watchlist.all(),
                "message": "Bid cannot be less than the starting or highest bid."
            })
        else:
            bid = Bid(value=value, bidder=request.user, listing=listing)
            bid.save()
            listing.highest_bid = value
            listing.save()
            return render(request, 'auctions/listing.html', {
                "listing": listing,
                "user_watchlist": request.user.watchlist.all(),
                "message": "Bid placed!"
            })


def close(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    winning_bid = Bid.objects.filter(
        listing=listing).order_by('-value').first()
    listing.winner = winning_bid.bidder
    listing.active = False
    listing.save()
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "message": "Listing closed!"
    })
