from django.db import migrations, models

import pages.model_validators


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0023_retirementinputsmodel_pension_start_age"),
    ]

    operations = [
        migrations.AddField(
            model_name="generalinputsmodel",
            name="add_medical_bills",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="generalinputsmodel",
            name="monthly_medical_bills",
            field=models.FloatField(
                default=0,
                validators=[
                    pages.model_validators.validate_monthly_medical_bills,
                    pages.model_validators.decimal_validator,
                ],
            ),
        ),
    ]
