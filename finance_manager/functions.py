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


def get_user_contractors(user, key):
    contractors = Contractors.objects.filter(user=user.id)
    for contractor in contractors:
        contractor.name = decrypt(key, contractor.name.tobytes())
    contractors_list = [(contractor.id, contractor.name) for contractor in contractors]
    return contractors_list


def get_user_goods(user, key):
    goods = Goods.objects.filter(user=user.id)
    for item in goods:
        item.name = decrypt(key, item.name.tobytes())
    goods_list = [(item.id, item.name) for item in goods]
    return goods_list


def calculate_purchase_average_price(user, name, purchase_price_per_unit):
    goods = Goods.objects.get(user=user, name=name)
    avg = goods.purchase_average_price
    count = goods.purchase_count
    avg = (avg * count) + purchase_price_per_unit
    count += 1
    avg = avg / count

    goods.purchase_average_price = avg
    goods.purchase_count = count
    goods.save()


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


def get_user_purchases(user, key):
    purchases = Purchases.objects.filter(user=user.id).order_by('-date')
    for purchase in purchases:
        purchase.contractor.name = decrypt(key, purchase.contractor.name)
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


def get_user_purchases_by_dates(user, key, date_from=None, date_to=None):
    if date_from is None:
        date_from = "1900-01-01"
    if date_to is None:
        date_to = date.today()
    purchases = Purchases.objects.filter(user=user.id, date__gte=date_from, date__lte=date_to).order_by('-date')
    for purchase in purchases:
        purchase.contractor.name = decrypt(key, purchase.contractor.name)
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


def on_stock_add(key, item, quantity):
    item = Goods.objects.get(id=item)
    item.on_stock = decrypt(key, item.on_stock)
    item.on_stock = Decimal(item.on_stock) + Decimal(quantity)
    item.on_stock = encrypt(key, item.on_stock)
    item.save()


def on_stock_remove(key, item, quantity):
    item = Goods.objects.get(id=item)
    item.on_stock = decrypt(key, item.on_stock)
    item.on_stock = Decimal(item.on_stock) - Decimal(quantity)
    item.on_stock = encrypt(key, item.on_stock)
    item.save()


def get_user_sales(user, key):
    sales = Sales.objects.filter(user=user.id).order_by('-date')
    for sale in sales:
        sale.contractor.name = decrypt(key, sale.contractor.name)
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


def get_user_sales_by_dates(user, key, date_from=None, date_to=None):
    if date_from is None:
        date_from = "1900-01-01"
    if date_to is None:
        date_to = date.today()
    sales = Sales.objects.filter(user=user.id, date__gte=date_from, date__lte=date_to).order_by('-date')
    for sale in sales:
        sale.contractor.name = decrypt(key, sale.contractor.name)
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


def get_user_extra_income(user, key):
    income = ExtraIncome.objects.filter(user_id=user.id)
    for money in income:
        money.name = decrypt(key, money.name)
        money.amount = decrypt(key, money.amount)
        money.description = decrypt(key, money.description)
    return income


def get_user_extra_income_by_date(user, key, date_from, date_to):
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


def get_last_30_days_income(user, key):
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


def get_user_extra_expenses(user, key):
    expenses = ExtraExpenses.objects.filter(user_id=user.id)
    for money in expenses:
        money.name = decrypt(key, money.name)
        money.amount = decrypt(key, money.amount)
        money.description = decrypt(key, money.description)
    return expenses


def get_user_extra_expenses_by_date(user, key, date_from, date_to):
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


def get_last_30_days_expenses(user, key):
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


def get_user_contractor_sales(user, key, contractor):
    sales = Sales.objects.filter(user_id=user.id, contractor_id=contractor).order_by('-date')
    for sale in sales:
        sale.contractor.name = decrypt(key, sale.contractor.name)
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


def get_user_contractor_purchases(user, key, contractor):
    purchases = Purchases.objects.filter(user_id=user.id, contractor_id=contractor).order_by('-date')
    for purchase in purchases:
        purchase.contractor.name = decrypt(key, purchase.contractor.name)
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
