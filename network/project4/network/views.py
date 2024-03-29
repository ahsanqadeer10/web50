import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators import csrf
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import EmptyPage, Paginator

from .models import User, Post


def index(request):
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 10)
    posts_page = None
    if request.GET.get("page") is None or int(request.GET.get("page")) < 1:
        posts_page = paginator.page(1)
    elif int(request.GET.get("page")) > paginator.num_pages:
        posts_page = paginator.page(paginator.num_pages)
    else:
        posts_page = paginator.page(int(request.GET.get("page")))
    for post in posts_page:
        post.like_count = post.likes.all().count
        if request.user.is_authenticated:
            post.user_likes = request.user in post.likes.all() 

    return render(request, "network/index.html", {
        "posts_page": posts_page
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Get profile picture
        profile_picture = None
        if request.FILES:
            profile_picture = request.FILES["profile-picture"]

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.profile_picture = profile_picture
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def post(request):
    if request.method == "POST" and request.user.is_authenticated:
        content = request.POST["content"]
        try:
            post = Post(content=content, author=request.user)
            post.save()
            return HttpResponseRedirect(reverse(index))
        except Exception:
            return HttpResponse("Could not create post.")
    return HttpResponse("post route hit")


@login_required
def post_edit(request, post_id):
    if request.method == "PUT":
        post = Post.objects.get(id=post_id)
        if request.user != post.author:
            return HttpResponse("Could not edit post.")
        data = json.loads(request.body)
        modified_content = data.get("modified_content")
        try:
            post.content = modified_content
            post.save()
        except Exception:
            return HttpResponse("Could not edit post.")
        return JsonResponse({
            "message": "success"
        }, status=200)


@login_required
def post_like(request, post_id):
    user = request.user
    post = Post.objects.get(pk=post_id)
    if user in post.likes.all():
        return HttpResponse("Something is wrong. Could not like post.")
    try:
        post.likes.add(user)
        post.save()
    except Exception:
        return HttpResponse("Something is wrong. Could not like post.")
    return JsonResponse({"message": "success", "like_count": post.likes.count()}, status=200)


@login_required
def post_unlike(request, post_id):
    user = request.user
    post = Post.objects.get(pk=post_id)
    if user not in post.likes.all():
        return HttpResponse("Something is wrong. Could not unlike post.")
    try:
        post.likes.remove(user)
        post.save()
    except Exception:
        return HttpResponse("Something is wrong. Could not unlike post.")
    return JsonResponse({"message": "success", "like_count": post.likes.count()}, status=200)


@login_required
def post_delete(request, post_id):
    user = request.user
    post = Post.objects.get(pk=post_id)
    if user != post.author:
        return JsonResponse({"message": "failed"})
    try:
        post.delete()
    except Exception:
        return JsonResponse({"message": "failed"})
    messages.success(request, 'Post deletion successful')  
    return JsonResponse({"message": "success"}, status=200)



def profile(request, username):
    try:
        profile = User.objects.get(username=username)
        posts = profile.posts.all().order_by('-created_at')
        paginator = Paginator(posts, 10)
        posts_page = None
        if request.GET.get("page") is None:
            posts_page = paginator.page(1)
        elif int(request.GET.get("page")) not in paginator.page_range:
            return HttpResponse("Page does not exist.")
        else:
            posts_page = paginator.page(int(request.GET.get("page")))
        following = None
        if request.user.is_authenticated:
            following = profile in request.user.following.all()
        for post in posts_page:
            post.like_count = post.likes.all().count
            if request.user.is_authenticated:
                post.user_likes = request.user in post.likes.all()
        return render(request, "network/profile.html", {
        "profile": profile,
        "followers_count": profile.followers.count(),
        "following_count": profile.following.count(),
        "posts_page": posts_page,
        "following": following
        })
    except Exception:
        return HttpResponse("Profile not found.")


@login_required
@csrf_exempt
def follow_toggle(request, username):
    if request.method == "PUT":
        try:
            source = User.objects.get(pk=request.user.id)
            target = User.objects.get(username=username)
            data = json.loads(request.body)
            following = data.get("following")
            if following == "false":
                target.followers.add(source)
            elif following == "true":
                target.followers.remove(source)
            target.save()
            return JsonResponse({
                "following": "true" if following == "false" else "false",
                "followers_count": target.followers.count()
            }, status= 200)
        except Exception:
            return HttpResponse("Could not complete follow/unfollow request.")


@login_required
def following(request):
    user = User.objects.get(pk=request.user.id)
    following = user.following.all()
    posts = None
    for profile in following:
        if posts is None:
            posts = profile.posts.all()
        else:
            posts = posts | profile.posts.all()
    posts_page = None
    if posts is not None:
            posts = posts.order_by('-created_at')
            paginator = Paginator(posts, 10)
            if request.GET.get("page") is None:
                posts_page = paginator.page(1)
            elif int(request.GET.get("page")) not in paginator.page_range:
                return HttpResponse("Page does not exist.")
            else:
                posts_page = paginator.page(int(request.GET.get("page")))
            for post in posts_page:
                post.like_count = post.likes.all().count
                if request.user.is_authenticated:
                    post.user_likes = request.user in post.likes.all()
    
    return render(request, "network/following.html", {
        "posts_page": posts_page
    })