from django.contrib.auth.models import User
from Crypto.Cipher import AES
from Crypto import Random
import base64

from django.forms import formset_factory

from .models import *

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1:])]


def get_user_defined_units(user, key):
    units = UserDefinedUnits.objects.filter(user=user.id)
    for unit in units:
        unit.short_name, unit.full_name = decrypt(key, unit.short_name.tobytes()), \
                                          decrypt(key, unit.full_name.tobytes())
    units_list = [(unit.short_name, unit.full_name) for unit in units]
    return units_list


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
    output = str(output)
    output = output[2:-1]
    return output


def key_generator():
    key = Random.new().read(32)
    return key


def get_user_purchases(user, key):
    purchases = Purchases.objects.filter(user=user.id).order_by('date')
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
    print(item.on_stock)
    item.on_stock = int(item.on_stock) + int(quantity)
    item.on_stock = encrypt(key, item.on_stock)
    item.save()


def on_stock_remove(key, item, quantity):
    item = Goods.objects.get(id=item)
    item.on_stock = decrypt(key, item.on_stock)
    print(item.on_stock)
    item.on_stock = int(item.on_stock) - int(quantity)
    item.on_stock = encrypt(key, item.on_stock)
    item.save()


def get_user_sales(user, key):
    sales = Sales.objects.filter(user=user.id).order_by('date')
    print(sales)
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
