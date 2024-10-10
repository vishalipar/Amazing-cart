# Generated by Django 5.1.1 on 2024-10-06 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_remove_account_types_account_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="account",
            name="type",
            field=models.CharField(
                choices=[("user", "user"), ("business", "business")], max_length=20
            ),
        ),
    ]