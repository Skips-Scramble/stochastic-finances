from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0026_remove_pension_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="retirementinputsmodel",
            name="use_conservative_rates",
            field=models.BooleanField(
                default=False,
                help_text="Gradually reduce this account's interest rate toward 5% by age 90",
            ),
        ),
    ]
