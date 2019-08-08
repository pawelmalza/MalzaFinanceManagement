from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from finance_manager.forms import AddNoteForm
from finance_manager.functions import get_user_notes, Encryption
from finance_manager.models import Notes


class ViewNotesView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            key = request.session['key']
            data = get_user_notes(request.user, key)
            ctx = {"data": data, "view": "Notes"}
            return render(request, "finance_manager/notes_list.html", ctx)
        except KeyError:
            return redirect(reverse_lazy('load_key'))
        except SyntaxError:
            return redirect(reverse_lazy('load_key'))


class AddNotesView(LoginRequiredMixin, View):

    def get(self, request):
        form = AddNoteForm()
        ctx = {
            "form": form,
            "submit": "Add note",
            "view": "Notes"
        }
        return render(request, "finance_manager/generic_form.html", ctx)

    def post(self, request):
        form = AddNoteForm(request.POST)
        key = request.session['key']
        if form.is_valid():
            name = Encryption.encrypt(key, form.cleaned_data.get('name'))
            content = Encryption.encrypt(key, form.cleaned_data.get('content'))
            Notes.objects.create(user_id=request.user.id, name=name, content=content)
            return redirect(reverse_lazy('view_notes'))
        return render(request, "finance_manager/generic_form.html",
                      context={"form": form, "submit": "Add note", "message": "Incorect form", "view": "Notes"})


class DeleteNoteView(LoginRequiredMixin, View):

    def get(self, request, note_id):
        note = Notes.objects.get(id=note_id)
        if request.user == note.user:
            note.delete()
            return redirect(reverse_lazy('view_notes'))
        return redirect(reverse_lazy('view_notes'))
