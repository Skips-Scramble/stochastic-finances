# Generated by Django 5.1.1 on 2024-11-10 22:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0007_paymentsinputsmodel_recurring_purchase_inf_adj"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="paymentsinputsmodel",
            name="recurring_purchase_inf_adj",
        ),
    ]
