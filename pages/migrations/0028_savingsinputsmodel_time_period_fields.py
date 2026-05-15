from django.db import migrations, models

import pages.model_validators


class Migration(migrations.Migration):
    dependencies = [
        (
            "pages",
            "0027_retirementinputsmodel_use_conservative_rates_default_false",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="savingsinputsmodel",
            name="period_end_age_mos",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[pages.model_validators.validate_range_age_mos],
            ),
        ),
        migrations.AddField(
            model_name="savingsinputsmodel",
            name="period_end_age_yrs",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[pages.model_validators.validate_range_age_yrs],
            ),
        ),
        migrations.AddField(
            model_name="savingsinputsmodel",
            name="period_start_age_mos",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[pages.model_validators.validate_range_age_mos],
            ),
        ),
        migrations.AddField(
            model_name="savingsinputsmodel",
            name="period_start_age_yrs",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[pages.model_validators.validate_range_age_yrs],
            ),
        ),
        migrations.AddField(
            model_name="savingsinputsmodel",
            name="time_period_mode",
            field=models.CharField(
                blank=True,
                choices=[
                    ("until", "Use this until"),
                    ("during", "Use this during"),
                    ("from", "Use this from"),
                ],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="savingsinputsmodel",
            name="use_time_period",
            field=models.BooleanField(
                default=False,
                help_text="Only use these assumptions for a given time period",
            ),
        ),
    ]
