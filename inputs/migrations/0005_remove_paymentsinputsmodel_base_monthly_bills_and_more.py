# Generated by Django 4.2.7 on 2024-01-07 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inputs", "0004_retirementinputsmodel_ratesinputsmodel"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="paymentsinputsmodel",
            name="base_monthly_bills",
        ),
        migrations.AddField(
            model_name="savingsinputsmodel",
            name="base_monthly_bills",
            field=models.FloatField(default=100),
            preserve_default=False,
        ),
    ]
