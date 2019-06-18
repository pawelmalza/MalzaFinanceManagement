from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import *
from django.views import View


class LoginView(View):

    def get(self, request):
        form = LoginFrom()
        ctx = {'form': form}
        return render(request, "finance_manager/login_form.html", ctx)

    def post(self, request):
        form = LoginFrom(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('login')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse_lazy('load_key'))
            else:
                return HttpResponse("Zle dane")


class LoadEncryptionKeView(View):

    def get(self, request):
        form = LoadEncryptionKeyForm
        ctx = {
            "form": form,
            "submit": "Load Key"
        }
        return render(request, "finance_manager/key_load_form.html", ctx)

    def post(self, request):
        form = LoadEncryptionKeyForm(request.POST, request.FILES)
        if form.is_valid():
            encryption_key = request.FILES['encryption_key'].read()
            print(encryption_key)
            print(len(encryption_key))
            request.session['key'] = encryption_key
            crash_test = request.session['key']
            print(crash_test)
            print(len(crash_test))
            return redirect(reverse_lazy('main_screen'))
        else:
            return HttpResponse("dupa")


class MainScreenView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, "finance_manager/main_screen.html")


class AddGoodsView(LoginRequiredMixin, View):

    def get(self, request):
        formset = AddGoodsFormset(request.GET or None)
        ctx = {
            "formset": formset,
            "submit": "Add"
        }
        return render(request, "finance_manager/dynamic_form.html", ctx)

    def post(self, request):
        formset = AddGoodsFormset(request.POST)
        if formset.is_valid():
            for form in formset:
                name = form.cleaned_data.get('name')
                on_stock = form.cleaned_data.get('on_stock')
                units = form.cleaned_data.get('units')
                user_id = request.user.id
                Goods.objects.create(user_id=user_id, name=name, on_stock=on_stock, units=units)
            return redirect(reverse_lazy('main_screen'))
        else:
            return HttpResponse(len(formset))
