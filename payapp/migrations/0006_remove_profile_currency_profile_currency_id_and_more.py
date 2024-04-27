# Generated by Django 5.0.4 on 2024-04-27 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payapp', '0005_rename_currency_id_profile_currency_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='currency',
        ),
        migrations.AddField(
            model_name='profile',
            name='currency_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone',
            field=models.CharField(blank=True, default=200, max_length=12, null=True),
        ),
    ]
