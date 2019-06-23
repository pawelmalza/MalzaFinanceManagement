from django.contrib.auth.models import User
from Crypto.Cipher import AES
from Crypto import Random
import base64
import os
from .models import *
from tempfile import NamedTemporaryFile

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1:])]


def get_user_defined_units(user):
    imported_dict = UserDefinedUnits.objects.filter(user=user.id)
    units_list = [(dict_item.short_name, dict_item.full_name) for dict_item in imported_dict]
    return units_list


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
