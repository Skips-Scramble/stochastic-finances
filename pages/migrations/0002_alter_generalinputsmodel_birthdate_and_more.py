# Generated by Django 5.0.1 on 2024-06-08 19:22

import pages.model_validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="generalinputsmodel",
            name="birthdate",
            field=models.DateField(
                validators=[pages.model_validators.validate_range_birthdate]
            ),
        ),
        migrations.AlterField(
            model_name="generalinputsmodel",
            name="retirement_age_mos",
            field=models.IntegerField(
                validators=[pages.model_validators.validate_range_age_mos]
            ),
        ),
        migrations.AlterField(
            model_name="generalinputsmodel",
            name="retirement_age_yrs",
            field=models.IntegerField(
                validators=[pages.model_validators.validate_range_age_yrs]
            ),
        ),
    ]