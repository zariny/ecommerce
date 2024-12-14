# Generated by Django 5.1.3 on 2024-12-14 18:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_productclassrelation_productclass_bases'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productclassrelation',
            name='base',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_relations', to='products.productclass'),
        ),
        migrations.AlterField(
            model_name='productclassrelation',
            name='subclass',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='base_relations', to='products.productclass'),
        ),
    ]
