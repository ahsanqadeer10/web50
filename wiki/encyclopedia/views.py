from django.forms.fields import CharField
from django.shortcuts import render
from django.http import HttpResponse
from django import forms

from . import util
import markdown2


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    entry = util.get_entry(title)
    if entry is None:
        return HttpResponse(f'The entry {title} does not exist.')
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title.capitalize(),
            "entry": markdown2.markdown(entry)
        })


def new(request):
    return HttpResponse("Add entry page")


def edit(request, title):
    return HttpResponse(f"Edit {title} page")


def search(request):
    if request.method == "POST":
        query = request.POST["q"]
        entry = util.get_entry(query)
        if entry is None:
            entries = util.list_entries()
            search_results = []
            for item in entries:
                if query in item:
                    search_results.append(item)
            print(search_results)
            return render(request, "encyclopedia/search.html", {
                "query": query,
                "search_results": search_results
            })
        else:
            return render(request, "encyclopedia/entry.html", {
                "title": query.capitalize(),
                "entry": markdown2.markdown(entry)
            })
