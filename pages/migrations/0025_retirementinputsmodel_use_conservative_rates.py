from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0024_add_medical_bills_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="retirementinputsmodel",
            name="use_conservative_rates",
            field=models.BooleanField(
                default=True,
                help_text="Gradually reduce this account's interest rate toward 5% by age 90",
            ),
        ),
    ]
