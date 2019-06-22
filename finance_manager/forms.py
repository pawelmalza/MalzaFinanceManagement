from django import forms
from django.forms import formset_factory

from .models import *
from finance_manager.validators import file_size_validator


class LoginFrom(forms.Form):
    login = forms.CharField(max_length=64)
    password = forms.CharField(max_length=64, widget=forms.PasswordInput)


class LoadEncryptionKeyForm(forms.Form):
    encryption_key = forms.FileField(validators=[file_size_validator])


class AddGoodsForm(forms.Form):

    name = forms.CharField()
    on_stock = forms.DecimalField()
    units = forms.CharField()


AddGoodsFormset = formset_factory(AddGoodsForm, extra=1)