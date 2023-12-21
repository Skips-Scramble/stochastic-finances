# Generated by Django 4.2.7 on 2023-12-21 02:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("financial_situation", "0028_alter_generalinputsmodel_created_by_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="generalinputsmodel",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="general_inputs",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="generalinputsmodel",
            name="modified_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name="savingsinputsmodel",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="savings_inputs",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="savingsinputsmodel",
            name="modified_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
