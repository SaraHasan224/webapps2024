# Generated by Django 5.0.4 on 2024-04-27 09:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payapp', '0004_rename_user_id_profile_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='currency_id',
            new_name='currency',
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='currency_id',
        ),
        migrations.AddField(
            model_name='wallet',
            name='currency',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='wallet_currency', to='payapp.currency'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='receiver_curr_id',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_receiver_currency', to='payapp.currency'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='sender_curr_id',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_sender_currency', to='payapp.currency'),
        ),
    ]
