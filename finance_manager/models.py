from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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


class Purchases(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractors, on_delete=models.CASCADE)
    goods = models.ManyToManyField(Goods, through='PurchasesGoods')
    date = models.DateField()
    money = models.BinaryField()


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
    money = models.BinaryField()
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


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10, default="EUR")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
