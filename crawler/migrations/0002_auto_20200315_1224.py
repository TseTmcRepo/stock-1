# Generated by Django 3.0.3 on 2020-03-15 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='share',
            name='ticker',
            field=models.CharField(max_length=256, unique=True),
        ),
    ]
