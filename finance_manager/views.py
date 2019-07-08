from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .functions import *
import io
from .forms import *
from django.views import View


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


class MainScreenView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            goods = get_user_goods_table(request.user, request.session['key'])
            last_30_days_income = get_last_30_days_income(request.user, request.session['key'])
            last_30_days_expenses = get_last_30_days_expenses(request.user, request.session['key'])
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


class AddGoodsView(LoginRequiredMixin, View):

    def get(self, request):
        formset = AddGoodsFormset(request.GET or None)
        ctx = {
            "formset": formset,
            "submit": "Register Goods",
            "view": "Goods"
        }
        return render(request, "finance_manager/dynamic_form.html", ctx)

    def post(self, request):
        formset = AddGoodsFormset(request.POST)
        key = request.session['key']
        if formset.is_valid():
            for form in formset:
                name = form.cleaned_data.get('name')
                on_stock = form.cleaned_data.get('on_stock')
                units = form.cleaned_data.get('units')
                print(name)
                print(on_stock)
                print(units)
                if (name is not None) and (units is not None) and (on_stock is not None):
                    name = encrypt(key, name)
                    on_stock = encrypt(key, on_stock)
                    units = encrypt(key, units)
                    Goods.objects.create(user_id=request.user.id, name=name, on_stock=on_stock, units=units)
            return redirect(reverse_lazy('view_goods'))
        ctx = {
            "formset": formset,
            "submit": "Register Goods",
            "view": "Goods"
        }
        return render(request, "finance_manager/dynamic_form.html", ctx)


class ViewGoodsView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            goods = Goods.objects.filter(user_id=request.user.id)
            key = request.session['key']
            for item in goods:
                item.name = decrypt(key, item.name.tobytes())
                item.on_stock = decrypt(key, item.on_stock.tobytes())
                item.units = decrypt(key, item.units.tobytes())
            return render(request, "finance_manager/goods_list_template.html", {"goods": goods, "view": "Goods"})
        except KeyError:
            return redirect(reverse_lazy('load_key'))
        except SyntaxError:
            return redirect(reverse_lazy('load_key'))


class GenerateKeyView(LoginRequiredMixin, View):

    def get(self, request):
        generated_key = key_generator()
        generated_key = io.BytesIO(generated_key)
        response = HttpResponse(generated_key.read(), content_type='application/malza')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format("key.malza")
        return response


class ViewContractorsView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            contractors = Contractors.objects.filter(user_id=request.user.id)
            key = request.session['key']
            for contractor in contractors:
                contractor.name = decrypt(key, contractor.name.tobytes())
            return render(request, "finance_manager/contractors_list.html",
                          {"contractors": contractors, "view": "contractors"})
        except KeyError:
            return redirect(reverse_lazy('load_key'))
        except SyntaxError:
            return redirect(reverse_lazy('load_key'))


class AddContractorsView(LoginRequiredMixin, View):

    def get(self, request):
        formset = formset_factory(AddContractorForm)
        formset = formset(request.GET or None)
        ctx = {
            "formset": formset,
            "submit": "Register Contractor",
            "view": "contractors"
        }
        return render(request, "finance_manager/dynamic_form.html", ctx)

    def post(self, request):
        formset = AddContractorFormset(request.POST)
        key = request.session['key']
        if formset.is_valid():
            for form in formset:
                name = form.cleaned_data.get('name')
                if name is not None:
                    name = encrypt(key, name)
                    Contractors.objects.create(user_id=request.user.id, name=name)
            return redirect(reverse_lazy("view_contractors"))
        ctx = {
            "formset": formset,
            "submit": "Register Contractor",
            "view": "contractors"
        }
        return render(request, "finance_manager/dynamic_form.html", ctx)


class ViewPurchasesView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            key = request.session['key']
            form = SearchByDataForm()
            data = get_user_purchases(request.user, key)
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
            form = SearchByDataForm(request.POST)
            if form.is_valid():
                data = get_user_purchases_by_dates(request.user, key, form.cleaned_data.get('date_from'),
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
        contractors = get_user_contractors(request.user, request.session['key'])
        goods = get_user_goods(request.user, request.session['key'])
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
            on_stock_add(key, goods, quantity)
            price_per_unit = encrypt(key, price_per_unit)
            quantity = encrypt(key, quantity)
            PurchasesGoods.objects.create(purchase_id=purchase.id, goods_id=goods, price_per_unit=price_per_unit,
                                          quantity_bought=quantity)
        purchase.money = encrypt(key, purchase.money)
        purchase.save()
        return redirect(reverse_lazy("view_purchases"))


class ViewSalesView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            key = request.session['key']
            form = SearchByDataForm()
            data = get_user_sales(request.user, key)
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
            form = SearchByDataForm(request.POST)
            if form.is_valid():
                data = get_user_sales_by_dates(request.user, key, form.cleaned_data.get('date_from'),
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
        contractors = get_user_contractors(request.user, request.session['key'])
        goods = get_user_goods(request.user, request.session['key'])
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
            on_stock_remove(key, goods, quantity)
            price_per_unit = encrypt(key, price_per_unit)
            quantity = encrypt(key, quantity)
            SalesGoods.objects.create(sale_id=sale.id, goods_id=goods, price_per_unit=price_per_unit,
                                      quantity_sold=quantity)
        sale.money = encrypt(key, sale.money)
        sale.save()
        return redirect(reverse_lazy("view_sales"))


class ViewNotesView(View):

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


class AddNotesView(View):

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
            name = encrypt(key, form.cleaned_data.get('name'))
            content = encrypt(key, form.cleaned_data.get('content'))
            Notes.objects.create(user_id=request.user.id, name=name, content=content)
            return redirect(reverse_lazy('view_notes'))
        return render(request, "finance_manager/generic_form.html",
                      context={"form": form, "submit": "Add note", "message": "Incorect form", "view": "Notes"})


class ViewExtraIncomeView(View):

    def get(self, request):
        try:
            data = get_user_extra_income(request.user, request.session['key'])
            form = SearchByDataForm()
            ctx = {'form': form, "data": data, "view": "Extra Income"}
            return render(request, "finance_manager/template_extra_income_expenses.html", ctx)
        except KeyError:
            return redirect(reverse_lazy('load_key'))
        except SyntaxError:
            return redirect(reverse_lazy('load_key'))

    def post(self, request):
        try:
            key = request.session['key']
            form = SearchByDataForm(request.POST)
            if form.is_valid():
                data = get_user_extra_income_by_date(request.user, key,
                                                     form.cleaned_data.get('date_from'),
                                                     form.cleaned_data.get('date_to'))
                ctx = {'form': form, "data": data, "view": "Extra Income"}
                return render(request, "finance_manager/template_extra_income_expenses.html", ctx)
        except ValueError:
            return redirect(reverse_lazy('view_income'))


class AddExtraIncomeView(View):

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
            name = encrypt(key, form.cleaned_data.get('name'))
            date = form.cleaned_data.get('date')
            amount = encrypt(key, form.cleaned_data.get('amount'))
            description = encrypt(key, form.cleaned_data.get('description'))
            ExtraIncome.objects.create(user_id=request.user.id, name=name, date=date, amount=amount,
                                       description=description)
            return redirect(reverse_lazy('view_income'))
        ctx = {
            "form": form,
            "submit": "Register Additional Income",
            "view": "Extra Income"
        }
        return render(request, "finance_manager/generic_form.html", ctx)


class ViewExtraExpensesView(View):

    def get(self, request):
        try:
            data = get_user_extra_expenses(request.user, request.session['key'])
            form = SearchByDataForm()
            ctx = {'form': form, "data": data, "view": "Extra Expenses"}
            return render(request, "finance_manager/template_extra_income_expenses.html", ctx)
        except KeyError:
            return redirect(reverse_lazy('load_key'))
        except SyntaxError:
            return redirect(reverse_lazy('load_key'))

    def post(self, request):
        try:
            key = request.session['key']
            form = SearchByDataForm(request.POST)
            if form.is_valid():
                data = get_user_extra_expenses_by_date(request.user, key, form.cleaned_data.get('date_from'),
                                                       form.cleaned_data.get('date_to'))
                ctx = {'form': form, "data": data, "view": "Extra Expenses"}
                return render(request, "finance_manager/template_extra_income_expenses.html", ctx)
        except ValueError:
            return redirect(reverse_lazy('view_expenses'))


class AddExtraExpensesView(View):

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
            name = encrypt(key, form.cleaned_data.get('name'))
            date = form.cleaned_data.get('date')
            amount = encrypt(key, form.cleaned_data.get('amount'))
            description = encrypt(key, form.cleaned_data.get('description'))
            ExtraExpenses.objects.create(user_id=request.user.id, name=name, date=date, amount=amount,
                                         description=description)
            return redirect(reverse_lazy('view_expenses'))
        ctx = {
            "form": form,
            "submit": "Register Additional Expense",
            "view": "Extra Expenses"
        }
        return render(request, "finance_manager/generic_form.html", ctx)


class ViewContractorPurchasesAndSalesView(View):

    def get(self, request, contractor_id):
        try:
            key = request.session['key']
            purchases = get_user_contractor_purchases(request.user, key, contractor_id)
            sales = get_user_contractor_sales(request.user, key, contractor_id)
            view = f"{decrypt(key, Contractors.objects.get(id=contractor_id).name)} transactions"
            ctx = {
                'purchases': purchases,
                'sales': sales,
                'view': view
            }
            return render(request, 'finance_manager/contractor_transactions_list.html', ctx)
        except KeyError:
            return redirect(reverse_lazy('load_key'))
        except SyntaxError:
            return redirect(reverse_lazy('load_key'))


class DeleteContractorView(View):

    def get(self, request, contractor_id):
        contractor = Contractors.objects.get(id=contractor_id)
        if request.user == contractor.user:
            contractor.delete()
            return redirect(reverse_lazy('view_contractors'))
        return redirect(reverse_lazy('view_contractors'))


class ProfileSettingsView(View):

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
