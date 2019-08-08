from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import formset_factory
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from finance_manager.forms import AddContractorForm, AddContractorFormset
from finance_manager.functions import GetContractors, Encryption
from finance_manager.models import Contractors


class ViewContractorsView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            key = request.session['key']
            contractors = GetContractors.all(request.user, key)
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
                    name = Encryption.encrypt(key, name)
                    Contractors.objects.create(user_id=request.user.id, name=name)
            return redirect(reverse_lazy("view_contractors"))
        ctx = {
            "formset": formset,
            "submit": "Register Contractor",
            "view": "contractors"
        }
        return render(request, "finance_manager/dynamic_form.html", ctx)


class ViewContractorPurchasesAndSalesView(LoginRequiredMixin, View):

    def get(self, request, contractor_id):
        try:
            key = request.session['key']
            purchases = GetContractors.purchases(request.user, key, contractor_id)
            sales = GetContractors.sales(request.user, key, contractor_id)
            view = f"{Encryption.decrypt(key, Contractors.objects.get(id=contractor_id).name)} transactions"
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


class DeleteContractorView(LoginRequiredMixin, View):

    def get(self, request, contractor_id):
        contractor = Contractors.objects.get(id=contractor_id)
        if request.user == contractor.user:
            contractor.delete()
            return redirect(reverse_lazy('view_contractors'))
        return redirect(reverse_lazy('view_contractors'))
