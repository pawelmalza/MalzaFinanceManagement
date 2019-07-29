from ast import literal_eval
from decimal import *
from datetime import timedelta, date
from Crypto.Cipher import AES
from Crypto import Random
import base64
from .models import *
from django.utils.dateparse import parse_date


def get_user_notes(user, key):
    notes = Notes.objects.filter(user_id=user.id)
    for note in notes:
        note.name = Encryption.decrypt(key, note.name)
        note.content = Encryption.decrypt(key, note.content)
    return notes


class Encryption:

    @staticmethod
    def key_generator():
        key = Random.new().read(32)
        return key

    @staticmethod
    def encrypt(key, input_enc):
        input_enc = str(input_enc).strip()
        input_enc = input_enc.encode('utf-8')
        input_enc = Encryption.pad(str(input_enc))
        iv = Random.new().read(AES.block_size)
        aes = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + aes.encrypt(input_enc))

    @staticmethod
    def decrypt(key, output):
        output = base64.b64decode(output)
        iv = output[:16]
        aes = AES.new(key, AES.MODE_CBC, iv)
        output = Encryption.unpad(aes.decrypt(output))
        output = output[16:]
        output = str(output.decode('utf8'))
        output = literal_eval(output).decode()
        return output

    @staticmethod
    def pad(s):
        block_size = 16
        return s + (block_size - len(s) % block_size) * chr(block_size - len(s) % block_size)

    @staticmethod
    def unpad(s):
        return s[0:-ord(s[-1:])]


class GetPurchases:

    @staticmethod
    def all(user, key):
        purchases = Purchases.objects.filter(user=user.id).order_by('-date')
        for purchase in purchases:
            purchase.contractor.name = Encryption.decrypt(key, purchase.contractor.name)
            purchase.money = Encryption.decrypt(key, purchase.money)
            purchase.items = []
            for item in purchase.purchasesgoods_set.all():
                small_list = []
                item.goods.name = Encryption.decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = Encryption.decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_bought = Encryption.decrypt(key, item.quantity_bought)
                small_list.append(item.quantity_bought)
                purchase.items.append(small_list)
        return purchases

    @staticmethod
    def by_dates(user, key, date_from=None, date_to=None):
        if date_from is None:
            date_from = "1900-01-01"
        if date_to is None:
            date_to = date.today()
        purchases = Purchases.objects.filter(user=user.id, date__gte=date_from, date__lte=date_to).order_by('-date')
        for purchase in purchases:
            purchase.contractor.name = Encryption.decrypt(key, purchase.contractor.name)
            purchase.money = Encryption.decrypt(key, purchase.money)
            purchase.items = []
            for item in purchase.purchasesgoods_set.all():
                small_list = []
                item.goods.name = Encryption.decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = Encryption.decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_bought = Encryption.decrypt(key, item.quantity_bought)
                small_list.append(item.quantity_bought)
                purchase.items.append(small_list)
        return purchases

    @staticmethod
    def add_to_stock(key, item, quantity):
        item = Goods.objects.get(id=item)
        item.on_stock = Encryption.decrypt(key, item.on_stock)
        item.on_stock = Decimal(item.on_stock) + Decimal(quantity)
        item.on_stock = Encryption.encrypt(key, item.on_stock)
        item.save()

    @staticmethod
    def specific(user, key, purchase_id):
        purchase = Purchases.objects.get(id=purchase_id)
        if purchase.user == user:
            purchase.contractor.name = Encryption.decrypt(key, purchase.contractor.name)
            purchase.money = Encryption.decrypt(key, purchase.money)
            purchase.items = []
            for item in purchase.purchasesgoods_set.all():
                small_list = []
                item.goods.name = Encryption.decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = Encryption.decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_bought = Encryption.decrypt(key, item.quantity_bought)
                small_list.append(item.quantity_bought)
                purchase.items.append(small_list)
            return purchase
        pass


class GetSales:

    @staticmethod
    def all(user, key):
        sales = Sales.objects.filter(user=user.id).order_by('-date')
        for sale in sales:
            sale.contractor.name = Encryption.decrypt(key, sale.contractor.name)
            sale.money = Encryption.decrypt(key, sale.money)
            sale.items = []
            for item in sale.salesgoods_set.all():
                small_list = []
                item.goods.name = Encryption.decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = Encryption.decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_sold = Encryption.decrypt(key, item.quantity_sold)
                small_list.append(item.quantity_sold)
                sale.items.append(small_list)
        return sales

    @staticmethod
    def by_dates(user, key, date_from=None, date_to=None):
        if date_from is None:
            date_from = "1900-01-01"
        if date_to is None:
            date_to = date.today()
        sales = Sales.objects.filter(user=user.id, date__gte=date_from, date__lte=date_to).order_by('-date')
        for sale in sales:
            sale.contractor.name = Encryption.decrypt(key, sale.contractor.name)
            sale.money = Encryption.decrypt(key, sale.money)
            sale.items = []
            for item in sale.salesgoods_set.all():
                small_list = []
                item.goods.name = Encryption.decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = Encryption.decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_sold = Encryption.decrypt(key, item.quantity_sold)
                small_list.append(item.quantity_sold)
                sale.items.append(small_list)
        return sales

    @staticmethod
    def remove_from_stock(key, item, quantity):
        item = Goods.objects.get(id=item)
        item.on_stock = Encryption.decrypt(key, item.on_stock)
        item.on_stock = Decimal(item.on_stock) - Decimal(quantity)
        item.on_stock = Encryption.encrypt(key, item.on_stock)
        item.save()

    @staticmethod
    def specific(user, key, sale_id):
        sale = Sales.objects.get(id=sale_id)
        if sale.user == user:
            sale.contractor.name = Encryption.decrypt(key, sale.contractor.name)
            sale.money = Encryption.decrypt(key, sale.money)
            sale.items = []
            for item in sale.salesgoods_set.all():
                small_list = []
                item.goods.name = Encryption.decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = Encryption.decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_sold = Encryption.decrypt(key, item.quantity_sold)
                small_list.append(item.quantity_sold)
                sale.items.append(small_list)
            return sale
        pass


class GetIncome:

    @staticmethod
    def extra_all(user, key):
        income = ExtraIncome.objects.filter(user_id=user.id)
        for money in income:
            money.name = Encryption.decrypt(key, money.name)
            money.amount = Encryption.decrypt(key, money.amount)
            money.description = Encryption.decrypt(key, money.description)
        return income

    @staticmethod
    def extra_by_date(user, key, date_from, date_to):
        if date_from is None:
            date_from = "1900-01-01"
        if date_to is None:
            date_to = date.today()
        income = ExtraIncome.objects.filter(user_id=user.id, date__gte=date_from, date__lte=date_to)
        for money in income:
            money.name = Encryption.decrypt(key, money.name)
            money.amount = Encryption.decrypt(key, money.amount)
            money.description = Encryption.decrypt(key, money.description)
        return income

    @staticmethod
    def last_30_days(user, key):
        sales = Sales.objects.filter(user_id=user.id, date__gte=(date.today() - timedelta(30)))
        incomes = ExtraIncome.objects.filter(user_id=user.id, date__gte=(date.today() - timedelta(30)))
        last_30_days_income = 0
        for sale in sales:
            for price in sale.salesgoods_set.all():
                price.price_per_unit = Decimal(Encryption.decrypt(key, price.price_per_unit))
                price.quantity_sold = Decimal(Encryption.decrypt(key, price.quantity_sold))
                paid = price.price_per_unit * price.quantity_sold
                last_30_days_income += paid
        for income in incomes:
            last_30_days_income = last_30_days_income
            income.amount = Decimal(Encryption.decrypt(key, income.amount))
            last_30_days_income = last_30_days_income + income.amount
        return last_30_days_income


class GetExpenses:

    @staticmethod
    def extra_all(user, key):
        expenses = ExtraExpenses.objects.filter(user_id=user.id)
        for money in expenses:
            money.name = Encryption.decrypt(key, money.name)
            money.amount = Encryption.decrypt(key, money.amount)
            money.description = Encryption.decrypt(key, money.description)
        return expenses

    @staticmethod
    def extra_by_date(user, key, date_from, date_to):
        if date_from is None:
            date_from = "1900-01-01"
        if date_to is None:
            date_to = date.today()
        expenses = ExtraExpenses.objects.filter(user_id=user.id, date__gte=date_from, date__lte=date_to)
        for money in expenses:
            money.name = Encryption.decrypt(key, money.name)
            money.amount = Encryption.decrypt(key, money.amount)
            money.description = Encryption.decrypt(key, money.description)
        return expenses

    @staticmethod
    def last_30_days(user, key):
        purchases = Purchases.objects.filter(user_id=user.id, date__gte=(date.today() - timedelta(30)))
        expenses = ExtraExpenses.objects.filter(user_id=user.id, date__gte=(date.today() - timedelta(30)))
        last_30_days_income = 0
        for purchase in purchases:
            for price in purchase.purchasesgoods_set.all():
                price.price_per_unit = Decimal(Encryption.decrypt(key, price.price_per_unit))
                price.quantity_bought = Decimal(Encryption.decrypt(key, price.quantity_bought))
                paid = price.price_per_unit * price.quantity_bought
                last_30_days_income += paid
        for expense in expenses:
            last_30_days_income = last_30_days_income
            expense.amount = Decimal(Encryption.decrypt(key, expense.amount))
            last_30_days_income = last_30_days_income + expense.amount
        return last_30_days_income


class GetContractors:

    @staticmethod
    def all(user, key):
        contractors = Contractors.objects.filter(user_id=user.id)
        for contractor in contractors:
            contractor.name = Encryption.decrypt(key, contractor.name)
        return contractors

    @staticmethod
    def choices(user, key):
        contractors = Contractors.objects.filter(user=user.id)
        for contractor in contractors:
            contractor.name = Encryption.decrypt(key, contractor.name.tobytes())
        contractors_list = [(contractor.id, contractor.name) for contractor in contractors]
        return contractors_list

    @staticmethod
    def sales(user, key, contractor):
        sales = Sales.objects.filter(user_id=user.id, contractor_id=contractor).order_by('-date')
        for sale in sales:
            sale.contractor.name = Encryption.decrypt(key, sale.contractor.name)
            sale.money = Encryption.decrypt(key, sale.money)
            sale.items = []
            for item in sale.salesgoods_set.all():
                small_list = []
                item.goods.name = Encryption.decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = Encryption.decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_sold = Encryption.decrypt(key, item.quantity_sold)
                small_list.append(item.quantity_sold)
                sale.items.append(small_list)
        return sales

    @staticmethod
    def sales_by_dates(user, key, contractor, date_from=None, date_to=None):
        if date_from is None:
            date_from = "1900-01-01"
        if date_to is None:
            date_to = date.today()
        sales = Sales.objects.filter(user_id=user.id, contractor_id=contractor, date__gte=date_from,
                                     date__lte=date_to).order_by('-date')
        for sale in sales:
            sale.contractor.name = Encryption.decrypt(key, sale.contractor.name)
            sale.money = Encryption.decrypt(key, sale.money)
            sale.items = []
            for item in sale.salesgoods_set.all():
                small_list = []
                item.goods.name = Encryption.decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = Encryption.decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_sold = Encryption.decrypt(key, item.quantity_sold)
                small_list.append(item.quantity_sold)
                sale.items.append(small_list)
        return sales

    @staticmethod
    def purchases(user, key, contractor):
        purchases = Purchases.objects.filter(user_id=user.id, contractor_id=contractor).order_by('-date')
        for purchase in purchases:
            purchase.contractor.name = Encryption.decrypt(key, purchase.contractor.name)
            purchase.money = Encryption.decrypt(key, purchase.money)
            purchase.items = []
            for item in purchase.purchasesgoods_set.all():
                small_list = []
                item.goods.name = Encryption.decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = Encryption.decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_bought = Encryption.decrypt(key, item.quantity_bought)
                small_list.append(item.quantity_bought)
                purchase.items.append(small_list)
        return purchases

    @staticmethod
    def purchases_by_dates(user, key, contractor, date_from=None, date_to=None):
        if date_from is None:
            date_from = "1900-01-01"
        if date_to is None:
            date_to = date.today()
        purchases = Purchases.objects.filter(user_id=user.id, contractor_id=contractor, date__gte=date_from,
                                             date__lte=date_to).order_by('-date')
        for purchase in purchases:
            purchase.contractor.name = Encryption.decrypt(key, purchase.contractor.name)
            purchase.money = Encryption.decrypt(key, purchase.money)
            purchase.items = []
            for item in purchase.purchasesgoods_set.all():
                small_list = []
                item.goods.name = Encryption.decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = Encryption.decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_bought = Encryption.decrypt(key, item.quantity_bought)
                small_list.append(item.quantity_bought)
                purchase.items.append(small_list)
        return purchases


class GetGoods:

    @staticmethod
    def choices(user, key):
        goods = Goods.objects.filter(user=user.id)
        for item in goods:
            item.name = Encryption.decrypt(key, item.name.tobytes())
        goods_list = [(item.id, item.name) for item in goods]
        return goods_list

    @staticmethod
    def all(user, key):
        goods = Goods.objects.filter(user_id=user.id)
        for item in goods:
            item.name = Encryption.decrypt(key, item.name)
            item.on_stock = Encryption.decrypt(key, item.on_stock)
            item.units = Encryption.decrypt(key, item.units)
        return goods

    @staticmethod
    def specific(user,key, goods_id):
        item = Goods.objects.get(id=goods_id)
        if item.user_id == user.id:
            item.name = Encryption.decrypt(key, item.name)
            item.on_stock = Encryption.decrypt(key, item.on_stock)
            item.units = Encryption.decrypt(key, item.units)
            return item


    @staticmethod
    def purchased(user, key, goods, date_from=None, date_to=None):
        if date_from is None:
            date_from = parse_date("1900-01-01")
        if date_to is None:
            date_to = date.today()
        k = PurchasesGoods.objects.filter(goods=goods)
        total_paid = Decimal(0)
        data = []
        for i in k:
            if (i.purchase.date >= date_from) and (i.purchase.date <= date_to):
                purchase = GetPurchases.specific(user, key, i.purchase.id)
                purchase.for_product = Decimal(Encryption.decrypt(key, i.price_per_unit)) * Decimal(
                    Encryption.decrypt(key, i.quantity_bought))
                total_paid += purchase.for_product
                data.append(purchase)
        return [data, total_paid]

    @staticmethod
    def sold(user, key, goods, date_from=None, date_to=None):
        if date_from is None:
            date_from = parse_date("1900-01-01")
        if date_to is None:
            date_to = date.today()
        k = SalesGoods.objects.filter(goods=goods)
        total_earned = Decimal(0)
        data = []
        for i in k:
            if (i.sale.date >= date_from) and (i.sale.date <= date_to):
                sale = GetSales.specific(user, key, i.sale.id)
                sale.for_product = Decimal(Encryption.decrypt(key, i.price_per_unit)) * Decimal(
                    Encryption.decrypt(key, i.quantity_sold))
                total_earned += sale.for_product
                data.append(sale)
        return [data, total_earned]


class Utils:

    @staticmethod
    def balance(income, expenses):
        return income - expenses

    @staticmethod
    def profit(income, expenses):
        if Utils.balance(income, expenses) < 0:
            return income / expenses * 100 * -1
        elif Utils.balance(income, expenses) == 0:
            return 0
        else:
            return income / expenses * 100
