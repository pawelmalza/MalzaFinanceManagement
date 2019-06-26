# Generated by Django 2.2.2 on 2019-06-26 07:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contractors',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.BinaryField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Goods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.BinaryField()),
                ('on_stock', models.BinaryField()),
                ('units', models.BinaryField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Purchases',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('contractor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance_manager.Contractors')),
            ],
        ),
        migrations.CreateModel(
            name='Sales',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('contractor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance_manager.Contractors')),
            ],
        ),
        migrations.CreateModel(
            name='UserDefinedUnits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.BinaryField()),
                ('full_name', models.BinaryField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SalesGoods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_per_unit', models.BinaryField()),
                ('quantity_sold', models.BinaryField()),
                ('goods', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance_manager.Goods')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance_manager.Sales')),
            ],
        ),
        migrations.AddField(
            model_name='sales',
            name='goods',
            field=models.ManyToManyField(through='finance_manager.SalesGoods', to='finance_manager.Goods'),
        ),
        migrations.AddField(
            model_name='sales',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='PurchasesGoods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_per_unit', models.BinaryField()),
                ('quantity_bought', models.BinaryField()),
                ('goods', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance_manager.Goods')),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance_manager.Purchases')),
            ],
        ),
        migrations.AddField(
            model_name='purchases',
            name='goods',
            field=models.ManyToManyField(through='finance_manager.PurchasesGoods', to='finance_manager.Goods'),
        ),
        migrations.AddField(
            model_name='purchases',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Notes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.BinaryField()),
                ('content', models.BinaryField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AdditionalIncome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.BinaryField()),
                ('date', models.DateField()),
                ('amount', models.BinaryField()),
                ('description', models.BinaryField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AdditionalExpenses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.BinaryField()),
                ('date', models.DateField()),
                ('amount', models.BinaryField()),
                ('description', models.BinaryField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
