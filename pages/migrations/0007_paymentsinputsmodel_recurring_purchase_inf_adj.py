# Generated by Django 5.1.1 on 2024-11-03 17:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0006_paymentsinputsmodel_recurring_length"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentsinputsmodel",
            name="recurring_purchase_inf_adj",
            field=models.BooleanField(default=False),
        ),
    ]