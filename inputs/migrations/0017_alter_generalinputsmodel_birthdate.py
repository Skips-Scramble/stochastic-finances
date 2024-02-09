# Generated by Django 4.2.7 on 2024-02-09 01:26

from django.db import migrations, models
import inputs.models


class Migration(migrations.Migration):

    dependencies = [
        ("inputs", "0016_alter_generalinputsmodel_retirement_age_mos_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="generalinputsmodel",
            name="birthdate",
            field=models.DateField(validators=[inputs.models.validate_range_birthdate]),
        ),
    ]
