from django.db import models
from django.contrib.auth.models import User


class UserDefinedUnits(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    short_name = models.CharField(max_length=10)
    full_name = models.CharField(max_length=255)


class Goods(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    on_stock = models.DecimalField(decimal_places=2, default=0, max_digits=9)
    units = models.CharField(max_length=255)
    purchase_average_price = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    purchase_count = models.IntegerField()
    sale_average_price = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    sale_count = models.IntegerField()


class Purchases(models.Model):
    goods = models.ManyToManyField(Goods)
    price_per_unit = models.DecimalField(decimal_places=2, max_digits=9)
    quantity_bought = models.DecimalField(decimal_places=2, default=1, max_digits=9)
    date = models.DateField()
    additional_costs = models.IntegerField()


class Sales(models.Model):
    goods = models.ManyToManyField(Goods)
    price_per_unit = models.DecimalField(decimal_places=2, max_digits=9)
    quantity_sold = models.DecimalField(decimal_places=2, default=1, max_digits=9)
    date = models.DateField()
    additional_income = models.IntegerField()
