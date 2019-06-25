from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from functools import wraps, partial
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from .functions import *
import io
from .forms import *
from django.views import View


class RegisterFormView(View):

    def get(self, request):
        form = RegisterForm()
        ctx = {
            "form": form,
            "submit": "register"
        }
        return render(request, "generic_form.html", ctx)

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
                "submit": "register"
            }
            return render(request, "generic_form.html", ctx)


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


class LoadEncryptionKeyView(LoginRequiredMixin, View):

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
            return redirect(reverse_lazy('view_goods'))
        else:
            return HttpResponse(len(formset))


class ViewGoodsView(LoginRequiredMixin, View):

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


class ViewContractorsView(LoginRequiredMixin, View):

    def get(self, request):
        contractors = Contractors.objects.filter(user_id=request.user.id)
        key = request.session['key']
        for contractor in contractors:
            contractor.name = decrypt(key, contractor.name.tobytes())
        return render(request, "finance_manager/contractors_list.html", {"contractors": contractors})


class AddContractorsView(LoginRequiredMixin, View):

    def get(self, request):
        formset = formset_factory(AddContractorForm)
        formset = formset(request.GET or None)
        ctx = {
            "formset": formset,
            "submit": "Add"
        }
        return render(request, "finance_manager/dynamic_form.html", ctx)

    def post(self, request):
        formset = AddContractorFormset(request.POST)
        key = request.session['key']
        if formset.is_valid():
            for form in formset:
                name = encrypt(key, form.cleaned_data.get('name'))
                Contractors.objects.create(user_id=request.user.id, name=name)
            return redirect(reverse_lazy("view_contractors"))
        return redirect(reverse_lazy("add_contractors"))


class ViewPurchasesView(LoginRequiredMixin, View):

    def get(self, request):
        key = request.session['key']
        data = get_user_purchases(request.user, key)
        ctx = {
            "obj_list": data
        }
        return render(request, "finance_manager/purchases_list.html", ctx)


class AddPurchaseView(LoginRequiredMixin, View):

    def get(self, request):
        contractors = get_user_contractors(request.user, request.session['key'])
        goods = get_user_goods(request.user, request.session['key'])
        form = SelectContractorAndDateForm(contractors=contractors)
        formset = AddPurchaseAndSaleFormset(request.GET or None, form_kwargs={"goods": goods})

        ctx = {
            "form": form,
            "formset": formset,
            "submit": "add"
        }
        return render(request, "finance_manager/purchase_and_sale_form.html", ctx)

    def post(self, request):
        key = request.session['key']
        date = request.POST.get('date')
        contractor = request.POST.get('contractor')
        print(request.POST)
        forms_number = int(request.POST.get('form-TOTAL_FORMS'))
        purchase = Purchases.objects.create(user_id=request.user.id, contractor_id=contractor, date=date)
        for i in range(0, forms_number):
            goods = request.POST.get(f'form-{i}-goods')
            price_per_unit = request.POST.get(f'form-{i}-price_per_unit')
            quantity = request.POST.get(f'form-{i}-quantity')
            on_stock_add(key, goods, quantity)
            price_per_unit = encrypt(key, price_per_unit)
            quantity = encrypt(key, quantity)
            PurchasesGoods.objects.create(purchase_id=purchase.id, goods_id=goods, price_per_unit=price_per_unit,
                                          quantity_bought=quantity)
        return redirect(reverse_lazy("view_purchases"))


class ViewSalesView(LoginRequiredMixin, View):

    def get(self, request):
        key = request.session['key']
        data = get_user_sales(request.user, key)
        print(data)
        ctx = {
            "obj_list": data
        }
        return render(request, "finance_manager/sales_list.html", ctx)


class AddSaleView(LoginRequiredMixin, View):

    def get(self, request):
        contractors = get_user_contractors(request.user, request.session['key'])
        goods = get_user_goods(request.user, request.session['key'])
        form = SelectContractorAndDateForm(contractors=contractors)
        formset = AddPurchaseAndSaleFormset(request.GET or None, form_kwargs={"goods": goods})

        ctx = {
            "form": form,
            "formset": formset,
            "submit": "add"
        }
        return render(request, "finance_manager/purchase_and_sale_form.html", ctx)

    def post(self, request):
        key = request.session['key']
        date = request.POST.get('date')
        contractor = request.POST.get('contractor')
        forms_number = int(request.POST.get('form-TOTAL_FORMS'))
        sale = Sales.objects.create(user_id=request.user.id, contractor_id=contractor, date=date)
        for i in range(0, forms_number):
            goods = request.POST.get(f'form-{i}-goods')
            price_per_unit = request.POST.get(f'form-{i}-price_per_unit')
            quantity = request.POST.get(f'form-{i}-quantity')
            on_stock_remove(key, goods, quantity)
            price_per_unit = encrypt(key, price_per_unit)
            quantity = encrypt(key, quantity)
            SalesGoods.objects.create(sale_id=sale.id, goods_id=goods, price_per_unit=price_per_unit,
                                      quantity_sold=quantity)
        return redirect(reverse_lazy("view_sales"))
