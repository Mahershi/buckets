# Generated by Django 4.2.9 on 2024-01-07 05:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0005_userbucket"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userbucket",
            name="joined_at",
            field=models.DateField(default=datetime.date.today, verbose_name="Date"),
        ),
    ]
