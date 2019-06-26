from django.urls import path

from .views import *

urlpatterns = [
    path('', LoginView.as_view(), name="login_view"),
    path('register/', RegisterFormView.as_view(), name="register_view"),
    path('logout/', Logout.as_view(), name="logout_view"),
    path('load_key/', LoadEncryptionKeyView.as_view(), name="load_key"),
    path('generate_key/', GenerateKeyView.as_view(), name="generate_key"),
    path('main/', MainScreenView.as_view(), name="main_screen"),
    path('goods/', ViewGoodsView.as_view(), name="view_goods"),
    path('goods/add/', AddGoodsView.as_view(), name='add_goods'),
    path('contractors/', ViewContractorsView.as_view(), name='view_contractors'),
    path('contractors/add/', AddContractorsView.as_view(), name='add_contractors'),
    path('purchases/add/', AddPurchaseView.as_view(), name='add_purchase'),
    path('purchases/', ViewPurchasesView.as_view(), name='view_purchases'),
    path('sales/add/', AddSaleView.as_view(), name='add_sale'),
    path('sales/', ViewSalesView.as_view(), name='view_sales'),
    path('notes/', ViewNotesView.as_view(), name='view_notes'),
    path('notes/add/', AddNotesView.as_view(), name='add_notes'),
    path('income/', ViewExtraIncomeView.as_view(), name='view_income'),
    path('income/add/', AddExtraIncomeView.as_view(), name='add_income'),
    path('expenses/', ViewExtraExpensesView.as_view(), name='view_expenses'),
    path('expenses/add/', AddExtraExpensesView.as_view(), name='add_expenses'),
]