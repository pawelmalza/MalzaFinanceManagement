from django import forms
from django.forms import formset_factory
from finance_manager.validators import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class RegisterForm(forms.Form):
    email = forms.EmailField(validators=[validate_mail_exists])
    password = forms.CharField(max_length=255, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=255, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords not match")


class LoginFrom(forms.Form):
    login = forms.CharField(max_length=64)
    password = forms.CharField(max_length=64, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginFrom, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-group"
        self.helper.add_input(Submit('submit', 'Submit'))


class LoadEncryptionKeyForm(forms.Form):
    encryption_key = forms.FileField(validators=[file_size_validator])


class AddGoodsForm(forms.Form):
    name = forms.CharField()
    on_stock = forms.DecimalField()
    units = forms.CharField()


class AddContractorForm(forms.Form):
    name = forms.CharField()


class SelectContractorAndDateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.contractors = kwargs.pop('contractors')
        super(SelectContractorAndDateForm, self).__init__()
        self.fields['contractor'] = forms.ChoiceField(choices=self.contractors)

    contractor = forms.ChoiceField()
    date = forms.DateField()


class AddPurchaseAndSaleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.goods = kwargs.pop('goods')
        super(AddPurchaseAndSaleForm, self).__init__()
        self.fields['goods'] = forms.ChoiceField(choices=self.goods)

    goods = forms.ChoiceField()
    price_per_unit = forms.DecimalField()
    quantity = forms.DecimalField()


class AddNoteForm(forms.Form):
    name = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)


class AddExtraForm(forms.Form):
    name = forms.CharField()
    date = forms.DateField()
    amount = forms.DecimalField()
    description = forms.CharField(widget=forms.Textarea)


class SearchByDataForm(forms.Form):
    date_from = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'date_field'}))
    date_to = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'date_field'}))


AddGoodsFormset = formset_factory(AddGoodsForm, extra=1)
AddContractorFormset = formset_factory(AddContractorForm, extra=1)
AddPurchaseAndSaleFormset = formset_factory(AddPurchaseAndSaleForm, extra=1)
