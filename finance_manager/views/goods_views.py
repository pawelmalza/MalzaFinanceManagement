from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from finance_manager.forms import AddGoodsFormset, SearchByDateForm
from finance_manager.functions import Encryption, GetGoods, Utils
from finance_manager.models import Goods


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
                if (name is not None) and (units is not None) and (on_stock is not None):
                    name = Encryption.encrypt(key, name)
                    on_stock = Encryption.encrypt(key, on_stock)
                    units = Encryption.encrypt(key, units)
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
            key = request.session['key']
            goods = GetGoods.all(request.user, key)
            return render(request, "finance_manager/goods_list_template.html", {"goods": goods, "view": "Goods"})
        except KeyError:
            return redirect(reverse_lazy('load_key'))
        except SyntaxError:
            return redirect(reverse_lazy('load_key'))


class ViewGoodsDetailsView(LoginRequiredMixin, View):

    def get(self, request, goods_id):
        try:
            key = request.session['key']
            form = SearchByDateForm()
            item = GetGoods.specific(request.user, key, goods_id)
            purchased = GetGoods.purchased(request.user, key, goods_id)
            sold = GetGoods.sold(request.user, key, goods_id)
            balance = Utils.balance(sold[1], purchased[1])
            profit = round(Utils.profit(sold[1], purchased[1]), 2)
            ctx = {
                'form': form,
                'purchases': purchased[0],
                'sales': sold[0],
                'total_paid': purchased[1],
                'total_earned': sold[1],
                'balance': balance,
                'profit': profit,
                'item_data': item,
            }
            return render(request, 'finance_manager/goods_transactions_list.html', ctx)
        except KeyError:
            return redirect(reverse_lazy('load_key'))
        except SyntaxError:
            return redirect(reverse_lazy('load_key'))

    def post(self, request, goods_id):
        try:
            key = request.session['key']
            form = SearchByDateForm(request.POST)
            item = GetGoods.specific(request.user, key, goods_id)
            if form.is_valid():
                date_from = form.cleaned_data.get('date_from')
                date_to = form.cleaned_data.get('date_to')
                purchased = GetGoods.purchased(request.user, key, goods_id, date_from, date_to)
                sold = GetGoods.sold(request.user, key, goods_id, date_from, date_to)
                balance = Utils.balance(sold[1], purchased[1])
                profit = round(Utils.profit(sold[1], purchased[1]), 2)
                ctx = {
                    'form': form,
                    'purchases': purchased[0],
                    'sales': sold[0],
                    'total_paid': purchased[1],
                    'total_earned': sold[1],
                    'balance': balance,
                    'item_data': item,
                    'profit': profit,
                }
                return render(request, 'finance_manager/goods_transactions_list.html', ctx)
            return redirect(reverse_lazy('view_goods'))
        except KeyError:
            return redirect(reverse_lazy('view_goods'))
        except SyntaxError:
            return redirect(reverse_lazy('view_goods'))
