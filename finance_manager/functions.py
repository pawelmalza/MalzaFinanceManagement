from ast import literal_eval
from decimal import *
from datetime import timedelta, date
from Crypto.Cipher import AES
from Crypto import Random
import base64
from .models import *

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1:])]


def get_user_goods(user, key):
    goods = Goods.objects.filter(user=user.id)
    for item in goods:
        item.name = decrypt(key, item.name.tobytes())
    goods_list = [(item.id, item.name) for item in goods]
    return goods_list


def encrypt(key, input):
    input = str(input).strip()
    input = input.encode('utf-8')
    input = pad(str(input))
    iv = Random.new().read(AES.block_size)
    aes = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + aes.encrypt(input))


def decrypt(key, output):
    output = base64.b64decode(output)
    iv = output[:16]
    aes = AES.new(key, AES.MODE_CBC, iv)
    output = unpad(aes.decrypt(output))
    output = output[16:]
    output = str(output.decode('utf8'))
    output = literal_eval(output).decode()
    return output


def key_generator():
    key = Random.new().read(32)
    return key


def get_user_goods_table(user, key):
    goods = Goods.objects.filter(user_id=user.id)
    for item in goods:
        item.name = decrypt(key, item.name)
        item.on_stock = decrypt(key, item.on_stock)
        item.units = decrypt(key, item.units)
    return goods


def get_user_notes(user, key):
    notes = Notes.objects.filter(user_id=user.id)
    for note in notes:
        note.name = decrypt(key, note.name)
        note.content = decrypt(key, note.content)
    return notes


class GetPurchases:

    @staticmethod
    def all(user, key):
        purchases = Purchases.objects.filter(user=user.id).order_by('-date')
        for purchase in purchases:
            purchase.contractor.name = decrypt(key, purchase.contractor.name)
            purchase.money = decrypt(key, purchase.money)
            purchase.items = []
            for item in purchase.purchasesgoods_set.all():
                small_list = []
                item.goods.name = decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_bought = decrypt(key, item.quantity_bought)
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
            purchase.contractor.name = decrypt(key, purchase.contractor.name)
            purchase.money = decrypt(key, purchase.money)
            purchase.items = []
            for item in purchase.purchasesgoods_set.all():
                small_list = []
                item.goods.name = decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_bought = decrypt(key, item.quantity_bought)
                small_list.append(item.quantity_bought)
                purchase.items.append(small_list)
        return purchases

    @staticmethod
    def add_to_stock(key, item, quantity):
        item = Goods.objects.get(id=item)
        item.on_stock = decrypt(key, item.on_stock)
        item.on_stock = Decimal(item.on_stock) + Decimal(quantity)
        item.on_stock = encrypt(key, item.on_stock)
        item.save()


class GetSales:

    @staticmethod
    def all(user, key):
        sales = Sales.objects.filter(user=user.id).order_by('-date')
        for sale in sales:
            sale.contractor.name = decrypt(key, sale.contractor.name)
            sale.money = decrypt(key, sale.money)
            sale.items = []
            for item in sale.salesgoods_set.all():
                small_list = []
                item.goods.name = decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_sold = decrypt(key, item.quantity_sold)
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
            sale.contractor.name = decrypt(key, sale.contractor.name)
            sale.money = decrypt(key, sale.money)
            sale.items = []
            for item in sale.salesgoods_set.all():
                small_list = []
                item.goods.name = decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_sold = decrypt(key, item.quantity_sold)
                small_list.append(item.quantity_sold)
                sale.items.append(small_list)
        return sales

    @staticmethod
    def remove_from_stock(key, item, quantity):
        item = Goods.objects.get(id=item)
        item.on_stock = decrypt(key, item.on_stock)
        item.on_stock = Decimal(item.on_stock) - Decimal(quantity)
        item.on_stock = encrypt(key, item.on_stock)
        item.save()


class GetIncome:

    @staticmethod
    def extra_all(user, key):
        income = ExtraIncome.objects.filter(user_id=user.id)
        for money in income:
            money.name = decrypt(key, money.name)
            money.amount = decrypt(key, money.amount)
            money.description = decrypt(key, money.description)
        return income

    @staticmethod
    def extra_by_date(user, key, date_from, date_to):
        if date_from is None:
            date_from = "1900-01-01"
        if date_to is None:
            date_to = date.today()
        income = ExtraIncome.objects.filter(user_id=user.id, date__gte=date_from, date__lte=date_to)
        for money in income:
            money.name = decrypt(key, money.name)
            money.amount = decrypt(key, money.amount)
            money.description = decrypt(key, money.description)
        return income

    @staticmethod
    def last_30_days(user, key):
        sales = Sales.objects.filter(user_id=user.id, date__gte=(date.today() - timedelta(30)))
        incomes = ExtraIncome.objects.filter(user_id=user.id, date__gte=(date.today() - timedelta(30)))
        last_30_days_income = 0
        for sale in sales:
            for price in sale.salesgoods_set.all():
                price.price_per_unit = Decimal(decrypt(key, price.price_per_unit))
                price.quantity_sold = Decimal(decrypt(key, price.quantity_sold))
                paid = price.price_per_unit * price.quantity_sold
                last_30_days_income += paid
        for income in incomes:
            last_30_days_income = last_30_days_income
            income.amount = Decimal(decrypt(key, income.amount))
            last_30_days_income = last_30_days_income + income.amount
        return last_30_days_income


class GetExpenses:

    @staticmethod
    def extra_all(user, key):
        expenses = ExtraExpenses.objects.filter(user_id=user.id)
        for money in expenses:
            money.name = decrypt(key, money.name)
            money.amount = decrypt(key, money.amount)
            money.description = decrypt(key, money.description)
        return expenses

    @staticmethod
    def extra_by_date(user, key, date_from, date_to):
        if date_from is None:
            date_from = "1900-01-01"
        if date_to is None:
            date_to = date.today()
        expenses = ExtraExpenses.objects.filter(user_id=user.id, date__gte=date_from, date__lte=date_to)
        for money in expenses:
            money.name = decrypt(key, money.name)
            money.amount = decrypt(key, money.amount)
            money.description = decrypt(key, money.description)
        return expenses

    @staticmethod
    def last_30_days(user, key):
        purchases = Purchases.objects.filter(user_id=user.id, date__gte=(date.today() - timedelta(30)))
        expenses = ExtraExpenses.objects.filter(user_id=user.id, date__gte=(date.today() - timedelta(30)))
        last_30_days_income = 0
        for purchase in purchases:
            for price in purchase.purchasesgoods_set.all():
                price.price_per_unit = Decimal(decrypt(key, price.price_per_unit))
                price.quantity_bought = Decimal(decrypt(key, price.quantity_bought))
                paid = price.price_per_unit * price.quantity_bought
                last_30_days_income += paid
        for expense in expenses:
            last_30_days_income = last_30_days_income
            expense.amount = Decimal(decrypt(key, expense.amount))
            last_30_days_income = last_30_days_income + expense.amount
        return last_30_days_income


class GetContractors:

    @staticmethod
    def all(user, key):
        contractors = Contractors.objects.filter(user_id=user.id)
        for contractor in contractors:
            contractor.name = decrypt(key, contractor.name)
        return contractors

    @staticmethod
    def choices(user, key):
        contractors = Contractors.objects.filter(user=user.id)
        for contractor in contractors:
            contractor.name = decrypt(key, contractor.name.tobytes())
        contractors_list = [(contractor.id, contractor.name) for contractor in contractors]
        return contractors_list

    @staticmethod
    def sales(user, key, contractor):
        sales = Sales.objects.filter(user_id=user.id, contractor_id=contractor).order_by('-date')
        for sale in sales:
            sale.contractor.name = decrypt(key, sale.contractor.name)
            sale.money = decrypt(key, sale.money)
            sale.items = []
            for item in sale.salesgoods_set.all():
                small_list = []
                item.goods.name = decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_sold = decrypt(key, item.quantity_sold)
                small_list.append(item.quantity_sold)
                sale.items.append(small_list)
        return sales

    @staticmethod
    def purchases(user, key, contractor):
        purchases = Purchases.objects.filter(user_id=user.id, contractor_id=contractor).order_by('-date')
        for purchase in purchases:
            purchase.contractor.name = decrypt(key, purchase.contractor.name)
            purchase.money = decrypt(key, purchase.money)
            purchase.items = []
            for item in purchase.purchasesgoods_set.all():
                small_list = []
                item.goods.name = decrypt(key, item.goods.name)
                small_list.append(item.goods.name)
                item.price_per_unit = decrypt(key, item.price_per_unit)
                small_list.append(item.price_per_unit)
                item.quantity_bought = decrypt(key, item.quantity_bought)
                small_list.append(item.quantity_bought)
                purchase.items.append(small_list)
        return purchases
