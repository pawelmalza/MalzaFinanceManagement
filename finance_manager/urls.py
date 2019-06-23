from django.urls import path

from .views import *

urlpatterns = [
    path('', LoginView.as_view(), name="login_view"),
    path('load_key/', LoadEncryptionKeView.as_view(), name="load_key"),
    path('generate_key/', GenerateKeyView.as_view(), name="generate_key"),
    path('main/', MainScreenView.as_view(), name="main_screen"),
    path('goods/', DisplayGoodsView.as_view(), name="display_goods"),
    path('goods/add', AddGoodsView.as_view(), name='add_goods'),
]