from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0019_add_private_insurance_per_mo"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="generalinputsmodel",
            name="medicare_coverage_type",
        ),
        migrations.RemoveField(
            model_name="generalinputsmodel",
            name="private_insurance_per_mo",
        ),
        migrations.AddField(
            model_name="generalinputsmodel",
            name="include_pre_medicare_insurance",
            field=models.BooleanField(default=False),
        ),
    ]
