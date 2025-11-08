from django.db import migrations, models
from pages.model_validators import validate_retirement_extra_expenses, decimal_validator


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0001_initial"),  # Replace with your last migration
    ]

    operations = [
        # Add field to GeneralInputsModel
        migrations.AddField(
            model_name="generalinputsmodel",
            name="retirement_extra_expenses",
            field=models.FloatField(
                validators=[validate_retirement_extra_expenses, decimal_validator],
                null=True,  # Allow null initially for existing records
                default=0,  # Set a default value
            ),
        ),
        # Data migration
        migrations.RunPython(
            # Forward migration
            code=lambda apps, schema_editor: apps.get_model(
                "pages", "GeneralInputsModel"
            ).objects.update(
                retirement_extra_expenses=apps.get_model(
                    "pages", "RetirementInputsModel"
                )
                .objects.filter(is_active=True)
                .first()
                .retirement_extra_expenses
                if apps.get_model("pages", "RetirementInputsModel")
                .objects.filter(is_active=True)
                .exists()
                else 0
            ),
            # Reverse migration
            reverse_code=lambda apps, schema_editor: None,
        ),
        # Remove field from RetirementInputsModel
        migrations.RemoveField(
            model_name="retirementinputsmodel",
            name="retirement_extra_expenses",
        ),
    ]
