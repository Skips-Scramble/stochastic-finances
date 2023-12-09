# Generated by Django 4.2.7 on 2023-12-02 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("financial_situation", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TestCalc",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("current_savings_account", models.FloatField()),
                ("current_interest", models.FloatField()),
            ],
        ),
        migrations.DeleteModel(
            name="Category",
        ),
    ]