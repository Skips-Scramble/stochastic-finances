# Generated by Django 5.1.1 on 2024-10-31 00:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0004_paymentsinputsmodel_inflation_adj"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentsinputsmodel",
            name="recurring_purchase",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="paymentsinputsmodel",
            name="recurring_timeframe",
            field=models.CharField(
                choices=[("quarterly", "Quarterly"), ("yearly", "Yearly")],
                default="quarterly",
                max_length=12,
            ),
        ),
    ]
