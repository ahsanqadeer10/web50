from django.shortcuts import redirect, render
from django.http import HttpResponse
from django import forms

from . import util
import markdown2
import random


class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title")
    markdown = forms.CharField(label="Markdown", widget=forms.Textarea)


class EditEntryForm(forms.Form):
    markdown = forms.CharField(label="Markdown", widget=forms.Textarea)


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
            "title": title,
            "entry": markdown2.markdown(entry)
        })


def new(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            markdown = bytes(form.cleaned_data["markdown"], 'utf-8')
            entry = util.get_entry(title)
            if entry is None:
                util.save_entry(title, markdown)
                return redirect(f'/wiki/{title}')
            else:
                return render(request, "encyclopedia/new.html", {
                    "form": form,
                    "error_msg": "An entry with the title already exists. Please write a different title."
                })
        else:
            return render(request, "encyclopedia/new.html", {
                "form": form,
                "error_msg": "The form entry/entries are invalid. Please check again."
            })

    return render(request, "encyclopedia/new.html", {
        "form": NewEntryForm()
    })


def edit(request, title):
    if request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            markdown = bytes(form.cleaned_data["markdown"], 'utf-8')
            util.save_entry(title, markdown)
            return redirect(f"/wiki/{title}")
        else:
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "form": form,
                "error_msg": "The form entry/entries are invalid. Please check again."
            })

    entry = util.get_entry(title)
    if entry is None:
        return HttpResponse(f"The entry { title } does not exist.")
    form = EditEntryForm(initial={'markdown': entry})
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": form
    })


def search(request):
    if request.method == "POST":
        query = request.POST["q"]
        entry = util.get_entry(query)
        if entry is None:
            entries = util.list_entries()
            search_results = []
            for item in entries:
                if query.lower() in item.lower():
                    search_results.append(item)
            return render(request, "encyclopedia/search.html", {
                "query": query,
                "search_results": search_results
            })
        else:
            return render(request, "encyclopedia/entry.html", {
                "title": query.capitalize(),
                "entry": markdown2.markdown(entry)
            })


def randompage(request):
    randomentry = random.choice(util.list_entries())
    return redirect(f"/wiki/{randomentry}")
