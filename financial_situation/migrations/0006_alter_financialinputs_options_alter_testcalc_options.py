# Generated by Django 4.2.7 on 2023-12-03 14:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("financial_situation", "0005_financialinputs_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="financialinputs",
            options={"verbose_name_plural": "Fiancial_Inputs"},
        ),
        migrations.AlterModelOptions(
            name="testcalc",
            options={"verbose_name_plural": "Test_Calcs"},
        ),
    ]