# Generated by Django 5.1.3 on 2024-12-11 10:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_productattributetranslate_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductClassRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rels', to='products.productclass')),
                ('subclass', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.productclass')),
            ],
            options={
                'unique_together': {('base', 'subclass')},
            },
        ),
        migrations.AddField(
            model_name='productclass',
            name='bases',
            field=models.ManyToManyField(related_name='subclasses', through='products.ProductClassRelation', to='products.productclass'),
        ),
    ]
