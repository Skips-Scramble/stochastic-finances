# Generated by Django 4.2.7 on 2024-02-09 01:23

from django.db import migrations, models
import inputs.models


class Migration(migrations.Migration):

    dependencies = [
        ("inputs", "0014_alter_generalinputsmodel_retirement_age_yrs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="generalinputsmodel",
            name="retirement_age_mos",
            field=models.FloatField(validators=[inputs.models.validate_range_age_mos]),
        ),
        migrations.AlterField(
            model_name="generalinputsmodel",
            name="retirement_age_yrs",
            field=models.FloatField(validators=[inputs.models.validate_range_age_yrs]),
        ),
    ]
