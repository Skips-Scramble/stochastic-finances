# Generated by Django 4.2.7 on 2023-12-03 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "financial_situation",
            "0006_alter_financialinputs_options_alter_testcalc_options",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="financialinputs",
            name="input_dict",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]