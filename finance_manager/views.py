from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from .functions import *
import io
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
            request.session['key'] = encryption_key

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
        key = request.session['key']
        if formset.is_valid():
            for form in formset:
                name = encrypt(key, form.cleaned_data.get('name'))
                on_stock = encrypt(key, form.cleaned_data.get('on_stock'))
                units = encrypt(key, form.cleaned_data.get('units'))
                Goods.objects.create(user_id=request.user.id, name=name, on_stock=on_stock, units=units)
            return redirect(reverse_lazy('display_goods'))
        else:
            return HttpResponse(len(formset))


class DisplayGoodsView(LoginRequiredMixin, View):

    def get(self, request):
        goods = Goods.objects.filter(user_id=request.user.id)
        key = request.session['key']
        for item in goods:
            item.name = decrypt(key, item.name.tobytes())
            item.on_stock = decrypt(key, item.on_stock.tobytes())
            item.units = decrypt(key, item.units.tobytes())
        return render(request, "finance_manager/goods_list_template.html", {"goods": goods})


class GenerateKeyView(LoginRequiredMixin, View):

    def get(self, request):
        generated_key = key_generator()
        generated_key = io.BytesIO(generated_key)
        response = HttpResponse(generated_key.read(), content_type='application/malza')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format("key.malza")
        return response
