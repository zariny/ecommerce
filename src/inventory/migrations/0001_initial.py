# Generated by Django 5.2 on 2025-04-20 15:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0011_product_categories'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Date updated')),
                ('price_currency', models.CharField(choices=[('EUR', 'Euro'), ('USD', 'US dollar')], default='EUR', max_length=4)),
                ('price', models.PositiveIntegerField(blank=True, null=True)),
                ('num_in_stock', models.PositiveIntegerField(blank=True, null=True)),
                ('num_allocated', models.IntegerField(blank=True, null=True)),
                ('low_stock_threshold', models.PositiveIntegerField(blank=True, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stockrecords', to='products.product')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
