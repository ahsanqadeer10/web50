from django.contrib.auth import authenticate, get_user, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Category, Bid, Comment


def index(request):
    listings = Listing.objects.filter(active=True).order_by("-date_created")
    watchlist = None
    if request.user.is_authenticated:
        watchlist = request.user.watchlist.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
        "watchlist": watchlist
    })


def login_view(request):
    # Check if a user is already signed in
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    alert_messages = []

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
            alert_messages += [{"text": "Invalid username and/or password",
                                "type": "error-alert"}]

    return render(request, "auctions/login.html", {
        "alert_messages": alert_messages
    })


@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    alert_messages = []

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            alert_messages += [{"text": "Passwords do not match",
                                "type": "error-alert"}]
        else:
            # Attempt to create new user
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            except IntegrityError:
                alert_messages += [{"text": "Username already registered",
                                    "type": "error-alert"}]

    return render(request, "auctions/register.html", {
        "alert_messages": alert_messages
    })


@login_required(login_url='/login')
def create(request):
    categories = Category.objects.all()
    alert_messages = []

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = int(request.POST["starting_bid"])
        image = request.POST["image"]
        category = Category.objects.get(pk=int(request.POST["category"]))

        try:
            listing = Listing(title=title, description=description, starting_bid=starting_bid,
                              image=image, category=category, creator=request.user)
            listing.save()
            alert_messages += [{"text": "Listing created successfully.",
                                "type": "success-alert"}]
            return render(request, "auctions/listing.html", {"listing": listing, "watchlist": request.user.watchlist.all(),
                                                             "alert_messages": alert_messages})
        except Exception:
            alert_messages += [{"text": "Could not create listing.",
                                "type": "error-alert"}]

    return render(request, "auctions/create.html", {
        "categories": categories,
        "alert_messages": alert_messages
    })


def listing(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
        comments = Comment.objects.filter(
            listing=listing).order_by("-date_created")

    except Exception:
        return HttpResponse("Could not find listing.")
    watchlist = None
    if request.user.is_authenticated:
        watchlist = request.user.watchlist.all()
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "watchlist": watchlist
    })


@login_required(login_url='/login')
def watch(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
    except:
        return HttpResponse("Could not find listing.")

    user = get_user(request)
    if listing.creator == user:
        return HttpResponse("Listing could not be added to watchlist.")

    alert_messages = []
    try:
        user.watchlist.add(listing)
        user.save()
        alert_messages += [{
            "text": "Listing added to watchlist.",
                    "type": "success-alert"
        }]
    except:
        alert_messages += [{
            "text": "Listing could not be added to watchlist.",
            "type": "error-alert"
        }]

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist": user.watchlist.all(),
        "alert_messages": alert_messages
    })


@login_required(login_url='/login')
def unwatch(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Exception:
        return HttpResponse("Could not find listing.")

    user = get_user(request)
    if listing.creator == user:
        return HttpResponse("Listing could not be removed from watchlist.")

    alert_messages = []
    try:
        user.watchlist.remove(listing)
        user.save()
        alert_messages += [{
            "text": "Listing removed from watchlist.",
                    "type": "success-alert"
        }]
    except:
        alert_messages += [{
            "text": "Listing could not be removed from watchlist.",
            "type": "error-alert"
        }]

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist": user.watchlist.all(),
        "alert_messages": alert_messages
    })


@login_required(login_url='/login')
def bid(request, listing_id):
    if request.method == "POST":
        try:
            listing = Listing.objects.get(pk=listing_id)
        except Exception:
            return HttpResponse("Could not find listing.")

        user = get_user(request)
        if listing.creator == user:
            return HttpResponse("Could not place bid.")

        value = int(request.POST["value"])
        alert_messages = []
        if value <= listing.starting_bid or value <= listing.highest_bid if listing.highest_bid is not None else 0:
            alert_messages += [{
                "text": "Bid cannot be less than the starting or highest bid.",
                "type": "error-alert"
            }]
        else:
            try:
                bid = Bid(value=value, bidder=user, listing=listing)
                bid.save()
                listing.highest_bid = value
                listing.save()
                alert_messages = [{
                    "text": "Bid placed.",
                    "type": "success-alert"
                }]
            except Exception:
                alert_messages += [{
                    "text": "Could not placed bid.",
                    "type": "error-alert"
                }]
    return render(request, 'auctions/listing.html', {
        "listing": listing,
        "watchlist": user.watchlist.all(),
        "alert_messages": alert_messages
    })


@login_required(login_url='/login')
def close(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Exception:
        return HttpResponse("Could not find listing.")

    user = get_user(request)
    if listing.creator != user:
        return HttpResponse("Could not close listing.")

    try:
        highest_bid = Bid.objects.filter(
            listing=listing).order_by('-value').first()
    except Exception:
        return HttpResponse("Could not resolve highest bid.")

    alert_messages = []
    try:
        listing.winner = highest_bid.bidder
        listing.active = False
        listing.save()
        alert_messages += [{
            "text": "Listing closed.",
                    "type": "success-alert"
        }]
    except Exception:
        alert_messages += [{
            "text": "Could not close listing.",
            "type": "error-alert"
        }]
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist": user.watchlist.all(),
        "alert_messages": alert_messages
    })


@login_required(login_url='/login')
def comment(request, listing_id):
    if request.method == "POST":
        user = request.user
        text = request.POST["comment-text"]
        listing = Listing.objects.get(pk=listing_id)
        comment = Comment(text=text, author=user, listing=listing)
        comment.save()
        return HttpResponseRedirect(reverse("listing", args={listing_id: listing_id}))


@login_required(login_url='/login')
def comment_delete(request, listing_id, comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Exception:
        return HttpResponse("Could not find comment.")

    if request.user != comment.author:
        return HttpResponse("Could not delete comment.")

    try:
        comment.delete()
        return HttpResponseRedirect(reverse("listing", args={listing_id: listing_id}))
    except Exception:
        return HttpResponse("Could not delete comment.")


@login_required(login_url='/login')
def watchlist(request):
    user = get_user(request)
    return render(request, "auctions/watchlist.html", {
        "watchlist": user.watchlist.all()
    })


def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category(request, category_id):
    category = Category.objects.get(pk=category_id)
    listings = Listing.objects.filter(category=category_id, active=True)
    return render(request, "auctions/category.html", {
        "listings": listings,
        "category": category
    })
