# Generated by Django 5.0.4 on 2024-04-26 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payapp', '0007_alter_profile_currency_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='currency_id',
            field=models.IntegerField(null=True),
        ),
    ]
