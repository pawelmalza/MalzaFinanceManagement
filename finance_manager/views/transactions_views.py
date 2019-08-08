from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from finance_manager.forms import SearchByDateForm, SelectContractorAndDateForm, AddPurchaseAndSaleFormset, AddExtraForm
from finance_manager.functions import GetPurchases, GetContractors, GetGoods, Encryption, GetSales, GetIncome, \
    GetExpenses
from finance_manager.models import Purchases, PurchasesGoods, Sales, SalesGoods, ExtraIncome, ExtraExpenses


class ViewPurchasesView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            key = request.session['key']
            form = SearchByDateForm()
            data = GetPurchases.all(request.user, key)
            ctx = {
                'form': form,
                "obj_list": data,
                "view": "Purchases"
            }
            return render(request, "finance_manager/purchases_list.html", ctx)
        except KeyError:
            return redirect(reverse_lazy('load_key'))
        except SyntaxError:
            return redirect(reverse_lazy('load_key'))

    def post(self, request):
        try:
            key = request.session['key']
            form = SearchByDateForm(request.POST)
            if form.is_valid():
                data = GetPurchases.by_dates(request.user, key, form.cleaned_data.get('date_from'),
                                             form.cleaned_data.get('date_to'))
                ctx = {
                    "form": form,
                    "obj_list": data,
                    "view": "Purchases"
                }
                return render(request, "finance_manager/purchases_list.html", ctx)
        except ValueError:
            return redirect(reverse_lazy('view_purchases'))


class AddPurchaseView(LoginRequiredMixin, View):

    def get(self, request):
        contractors = GetContractors.choices(request.user, request.session['key'])
        goods = GetGoods.choices(request.user, request.session['key'])
        form = SelectContractorAndDateForm(contractors=contractors)
        formset = AddPurchaseAndSaleFormset(request.GET or None, form_kwargs={"goods": goods})

        ctx = {
            "form": form,
            "formset": formset,
            "submit": "Register Purchase",
            "view": "Purchases"
        }
        return render(request, "finance_manager/purchase_and_sale_form.html", ctx)

    def post(self, request):
        key = request.session['key']
        date = request.POST.get('date')
        contractor = request.POST.get('contractor')
        forms_number = int(request.POST.get('form-TOTAL_FORMS'))
        purchase = Purchases.objects.create(user_id=request.user.id, contractor_id=contractor, date=date)
        purchase.money = 0
        for i in range(0, forms_number):
            goods = request.POST.get(f'form-{i}-goods')
            price_per_unit = request.POST.get(f'form-{i}-price_per_unit')
            quantity = request.POST.get(f'form-{i}-quantity')
            purchase.money += Decimal(price_per_unit) * Decimal(quantity)
            GetPurchases.add_to_stock(key, goods, quantity)
            price_per_unit = Encryption.encrypt(key, price_per_unit)
            quantity = Encryption.encrypt(key, quantity)
            PurchasesGoods.objects.create(purchase_id=purchase.id, goods_id=goods, price_per_unit=price_per_unit,
                                          quantity_bought=quantity)
        purchase.money = Encryption.encrypt(key, purchase.money)
        purchase.save()
        return redirect(reverse_lazy("view_purchases"))


class ViewSalesView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            key = request.session['key']
            form = SearchByDateForm()
            data = GetSales.all(request.user, key)
            ctx = {
                "form": form,
                "obj_list": data,
                "view": "Sales"
            }
            return render(request, "finance_manager/sales_list.html", ctx)
        except KeyError:
            return redirect(reverse_lazy('load_key'))
        except SyntaxError:
            return redirect(reverse_lazy('load_key'))

    def post(self, request):
        try:
            key = request.session['key']
            form = SearchByDateForm(request.POST)
            if form.is_valid():
                data = GetSales.by_dates(request.user, key, form.cleaned_data.get('date_from'),
                                         form.cleaned_data.get('date_to'))
                ctx = {
                    "form": form,
                    "obj_list": data,
                    "view": "Sales"
                }
                return render(request, "finance_manager/sales_list.html", ctx)
        except ValueError:
            return redirect(reverse_lazy('view_sales'))


class AddSaleView(LoginRequiredMixin, View):

    def get(self, request):
        contractors = GetContractors.choices(request.user, request.session['key'])
        goods = GetGoods.choices(request.user, request.session['key'])
        form = SelectContractorAndDateForm(contractors=contractors)
        formset = AddPurchaseAndSaleFormset(request.GET or None, form_kwargs={"goods": goods})
        ctx = {
            "form": form,
            "formset": formset,
            "submit": "Register Sale",
            "view": "Sales"
        }
        return render(request, "finance_manager/purchase_and_sale_form.html", ctx)

    def post(self, request):
        key = request.session['key']
        date = request.POST.get('date')
        contractor = request.POST.get('contractor')
        forms_number = int(request.POST.get('form-TOTAL_FORMS'))
        sale = Sales.objects.create(user_id=request.user.id, contractor_id=contractor, date=date)
        sale.money = 0
        for i in range(0, forms_number):
            goods = request.POST.get(f'form-{i}-goods')
            price_per_unit = request.POST.get(f'form-{i}-price_per_unit')
            quantity = request.POST.get(f'form-{i}-quantity')
            sale.money += Decimal(price_per_unit) * Decimal(quantity)
            GetSales.remove_from_stock(key, goods, quantity)
            price_per_unit = Encryption.encrypt(key, price_per_unit)
            quantity = Encryption.encrypt(key, quantity)
            SalesGoods.objects.create(sale_id=sale.id, goods_id=goods, price_per_unit=price_per_unit,
                                      quantity_sold=quantity)
        sale.money = Encryption.encrypt(key, sale.money)
        sale.save()
        return redirect(reverse_lazy("view_sales"))


class ViewExtraIncomeView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            data = GetIncome.extra_all(request.user, request.session['key'])
            form = SearchByDateForm()
            ctx = {'form': form, "data": data, "view": "Extra Income"}
            return render(request, "finance_manager/template_extra_income_expenses.html", ctx)
        except KeyError:
            return redirect(reverse_lazy('load_key'))
        except SyntaxError:
            return redirect(reverse_lazy('load_key'))

    def post(self, request):
        try:
            key = request.session['key']
            form = SearchByDateForm(request.POST)
            if form.is_valid():
                data = GetIncome.extra_by_date(request.user, key,
                                               form.cleaned_data.get('date_from'),
                                               form.cleaned_data.get('date_to'))
                ctx = {'form': form, "data": data, "view": "Extra Income"}
                return render(request, "finance_manager/template_extra_income_expenses.html", ctx)
        except ValueError:
            return redirect(reverse_lazy('view_income'))


class AddExtraIncomeView(LoginRequiredMixin, View):

    def get(self, request):
        form = AddExtraForm()
        ctx = {
            "form": form,
            "submit": "Register Additional Income",
            "view": "Extra Income"
        }
        return render(request, "finance_manager/generic_form.html", ctx)

    def post(self, request):
        form = AddExtraForm(request.POST)
        key = request.session['key']
        if form.is_valid():
            name = Encryption.encrypt(key, form.cleaned_data.get('name'))
            date = form.cleaned_data.get('date')
            amount = Encryption.encrypt(key, form.cleaned_data.get('amount'))
            description = Encryption.encrypt(key, form.cleaned_data.get('description'))
            ExtraIncome.objects.create(user_id=request.user.id, name=name, date=date, amount=amount,
                                       description=description)
            return redirect(reverse_lazy('view_income'))
        ctx = {
            "form": form,
            "submit": "Register Additional Income",
            "view": "Extra Income"
        }
        return render(request, "finance_manager/generic_form.html", ctx)


class ViewExtraExpensesView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            data = GetExpenses.extra_all(request.user, request.session['key'])
            form = SearchByDateForm()
            ctx = {'form': form, "data": data, "view": "Extra Expenses"}
            return render(request, "finance_manager/template_extra_income_expenses.html", ctx)
        except KeyError:
            return redirect(reverse_lazy('load_key'))
        except SyntaxError:
            return redirect(reverse_lazy('load_key'))

    def post(self, request):
        try:
            key = request.session['key']
            form = SearchByDateForm(request.POST)
            if form.is_valid():
                data = GetExpenses.extra_by_date(request.user, key, form.cleaned_data.get('date_from'),
                                                 form.cleaned_data.get('date_to'))
                ctx = {'form': form, "data": data, "view": "Extra Expenses"}
                return render(request, "finance_manager/template_extra_income_expenses.html", ctx)
        except ValueError:
            return redirect(reverse_lazy('view_expenses'))


class AddExtraExpensesView(LoginRequiredMixin, View):

    def get(self, request):
        form = AddExtraForm()
        ctx = {
            "form": form,
            "submit": "Register Additional Expense",
            "view": "Extra Expenses"
        }
        return render(request, "finance_manager/generic_form.html", ctx)

    def post(self, request):
        form = AddExtraForm(request.POST)
        key = request.session['key']
        if form.is_valid():
            name = Encryption.encrypt(key, form.cleaned_data.get('name'))
            date = form.cleaned_data.get('date')
            amount = Encryption.encrypt(key, form.cleaned_data.get('amount'))
            description = Encryption.encrypt(key, form.cleaned_data.get('description'))
            ExtraExpenses.objects.create(user_id=request.user.id, name=name, date=date, amount=amount,
                                         description=description)
            return redirect(reverse_lazy('view_expenses'))
        ctx = {
            "form": form,
            "submit": "Register Additional Expense",
            "view": "Extra Expenses"
        }
        return render(request, "finance_manager/generic_form.html", ctx)


class DeletePurchaseView(LoginRequiredMixin, View):

    def get(self, request, purchase_id):
        purchase = Purchases.objects.get(id=purchase_id)
        if request.user == purchase.user:
            purchase.delete()
            return redirect(reverse_lazy('view_purchases'))
        return redirect(reverse_lazy('view_purchases'))


class DeleteSaleView(LoginRequiredMixin, View):

    def get(self, request, sale_id):
        sale = Sales.objects.get(id=sale_id)
        if request.user == sale.user:
            sale.delete()
            return redirect(reverse_lazy('view_sales'))
        return redirect(reverse_lazy('view_sales'))


class DeleteIncomeView(LoginRequiredMixin, View):

    def get(self, request, income_id):
        income = ExtraIncome.objects.get(id=income_id)
        if request.user == income.user:
            income.delete()
            return redirect(reverse_lazy('view_income'))
        return redirect(reverse_lazy('view_income'))


class DeleteExpenseView(LoginRequiredMixin, View):

    def get(self, request, expense_id):
        expense = ExtraExpenses.objects.get(id=expense_id)
        if request.user == expense.user:
            expense.delete()
            return redirect(reverse_lazy('view_expenses'))
        return redirect(reverse_lazy('view_expenses'))
