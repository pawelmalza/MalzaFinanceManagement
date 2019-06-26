from django.db import models
from django.contrib.auth.models import User


class Contractors(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.BinaryField()


class UserDefinedUnits(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    short_name = models.BinaryField()
    full_name = models.BinaryField()


class Goods(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.BinaryField()
    on_stock = models.BinaryField()
    units = models.BinaryField()
    # PROCENT PROFIT


class Purchases(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractors, on_delete=models.CASCADE)
    goods = models.ManyToManyField(Goods, through='PurchasesGoods')
    date = models.DateField()
    # DODAC DODATKOWE KOSZTY W FORMULARZU


class PurchasesGoods(models.Model):
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchases, on_delete=models.CASCADE)
    price_per_unit = models.BinaryField()
    quantity_bought = models.BinaryField()


class Sales(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractors, on_delete=models.CASCADE)
    goods = models.ManyToManyField(Goods, through='SalesGoods')
    date = models.DateField()
    # DODAC DODATKOWE KOSZTY W FORMULARZU


class SalesGoods(models.Model):
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE)
    price_per_unit = models.BinaryField()
    quantity_sold = models.BinaryField()


class ExtraExpenses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.BinaryField()
    date = models.DateField()
    amount = models.BinaryField()
    description = models.BinaryField()


class ExtraIncome(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.BinaryField()
    date = models.DateField()
    amount = models.BinaryField()
    description = models.BinaryField()


class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.BinaryField()
    content = models.BinaryField()
