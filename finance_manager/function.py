from django.contrib.auth.models import User

from .models import *


def get_user_defined_units(user):
    imported_dict = UserDefinedUnits.objects.filter(user=user.id)
    units_list = [(dict_item.short_name, dict_item.full_name) for dict_item in imported_dict]
    return units_list


def calculate_purchase_average_price(user, name, purchase_price_per_unit):
    goods = Goods.objects.get(user=user, name=name)
    avg = goods.purchase_average_price
    count = goods.purchase_count
    avg = (avg*count) + purchase_price_per_unit
    count += 1
    avg = avg/count

    goods.purchase_average_price = avg
    goods.purchase_count = count
    goods.save()
