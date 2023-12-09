# Generated by Django 4.2.7 on 2023-12-07 02:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("financial_situation", "0009_alter_financialinputs_birthday"),
    ]

    operations = [
        migrations.CreateModel(
            name="Person",
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
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Job",
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
                ("job_title", models.CharField(max_length=100)),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="financial_situation.person",
                    ),
                ),
            ],
        ),
    ]