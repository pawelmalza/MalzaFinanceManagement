from django.db import models
from django.contrib.auth.models import User


class UserDefinedUnits(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    short_name = models.CharField(max_length=10)
    full_name = models.CharField(max_length=255)


class Goods(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.BinaryField()
    on_stock = models.BinaryField()
    units = models.BinaryField()
    # PROCENT PROFIT


class Purchases(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goods = models.ManyToManyField(Goods)
    price_per_unit = models.DecimalField(decimal_places=2, max_digits=9)
    quantity_bought = models.DecimalField(decimal_places=2, default=1, max_digits=9)
    date = models.DateField()
    # DODAC DODATKOWE KOSZTY W FORMULARZU


class Sales(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goods = models.ManyToManyField(Goods)
    price_per_unit = models.DecimalField(decimal_places=2, max_digits=9)
    quantity_sold = models.DecimalField(decimal_places=2, default=1, max_digits=9)
    date = models.DateField()
    # DODAC DODATKOWE KOSZTY W FORMULARZU


class AddtionalCosts(models.Model):
    pass
