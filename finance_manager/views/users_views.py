import io

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from finance_manager.forms import RegisterForm, LoginFrom, LoadEncryptionKeyForm, ProfileSettingsForm
from finance_manager.functions import Encryption, GetGoods, GetIncome, GetExpenses


class RegisterFormView(View):

    def get(self, request):
        form = RegisterForm()
        ctx = {
            "form": form,
            "submit": "register",
            "view": "register"
        }
        return render(request, "finance_manager/register.html", ctx)

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User()
            user.set_password(form.cleaned_data.get('password'))
            user.email = form.cleaned_data.get('email')
            user.username = user.email
            user.save()
            return redirect(reverse_lazy('login_view'))
        else:
            message = "<h3>Please, correct your form</h3>"
            ctx = {
                "form": form,
                "message": message,
                "submit": "register",
                "view": "register"
            }
            return render(request, "finance_manager/register.html", ctx)


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
                return redirect(reverse_lazy('main_screen'))
            else:
                return render(request, "finance_manager/login_form.html", {'form': form})


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect(reverse_lazy('login_view'))


class LoadEncryptionKeyView(LoginRequiredMixin, View):

    def get(self, request):
        form = LoadEncryptionKeyForm
        ctx = {
            "form": form,
            "submit": "Load Key",
            "view": "Load Key"
        }
        return render(request, "finance_manager/key_load_form.html", ctx)

    def post(self, request):
        form = LoadEncryptionKeyForm(request.POST, request.FILES)
        if form.is_valid():
            encryption_key = request.FILES['encryption_key'].read()
            request.session['key'] = encryption_key

            return redirect(reverse_lazy('main_screen'))
        else:
            ctx = {
                "form": form,
                "submit": "Load Key",
                "view": "Load Key"
            }
            return render(request, "finance_manager/key_load_form.html", ctx)


class GenerateKeyView(LoginRequiredMixin, View):

    def get(self, request):
        generated_key = Encryption.key_generator()
        generated_key = io.BytesIO(generated_key)
        response = HttpResponse(generated_key.read(), content_type='application/malza')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format("key.malza")
        return response


class ProfileSettingsView(LoginRequiredMixin, View):

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        initial = {'currency': user.profile.currency}
        form = ProfileSettingsForm(initial=initial)
        return render(request, 'finance_manager/generic_form.html', {'form': form, 'submit': 'Set'})

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        form = ProfileSettingsForm(request.POST)
        if form.is_valid():
            currency = form.cleaned_data.get('currency')
            user.profile.currency = currency
            user.profile.save()
            return redirect(reverse_lazy('main_screen'))
        return redirect(reverse_lazy('settings'))


class MainScreenView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            goods = GetGoods.all(request.user, request.session['key'])
            last_30_days_income = GetIncome.last_30_days(request.user, request.session['key'])
            last_30_days_expenses = GetExpenses.last_30_days(request.user, request.session['key'])
            last_30_days_balance = last_30_days_income - last_30_days_expenses
            ctx = {
                'goods': goods,
                "view": "Dashboard",
                "last_30_days_income": last_30_days_income,
                "last_30_days_expenses": last_30_days_expenses,
                "last_30_days_balance": last_30_days_balance
            }
            return render(request, "finance_manager/base.html", ctx)
        except KeyError:
            return redirect(reverse_lazy('load_key'))
        except SyntaxError:
            return redirect(reverse_lazy('load_key'))
