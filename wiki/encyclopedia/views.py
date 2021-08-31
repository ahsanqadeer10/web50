from django.forms.fields import CharField
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django import forms

from . import util
import markdown2


class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title")
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
            "title": title.capitalize(),
            "entry": markdown2.markdown(entry)
        })


def new(request):
    if request.method == "POST":
        print("New entry form posted!")
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            markdown = form.cleaned_data["markdown"]
            entry = util.get_entry(title)
            if entry is None:
                util.save_entry(title, markdown)
                return redirect(f'wiki/{title}')
            else:
                return render(request, "encyclopedia/new.html", {
                    "form": form,
                    "error_msg": "An entry with the title already exists. Please write a different heading."
                })
        else:
            return render(request, "encyclopedia/new.html", {
                "form": form
            })

    return render(request, "encyclopedia/new.html", {
        "form": NewEntryForm()
    })


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
                if query.lower() in item.lower():
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
