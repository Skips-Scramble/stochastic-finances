# Generated by Django 4.2.7 on 2023-12-21 02:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("financial_situation", "0031_alter_generalinputsmodel_modified_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="generalinputsmodel",
            name="created_by",
            field=models.ForeignKey(
                default=django.utils.timezone.now,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="general_inputs",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
