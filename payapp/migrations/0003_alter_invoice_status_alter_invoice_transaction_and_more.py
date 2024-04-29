# Generated by Django 5.0.4 on 2024-04-29 09:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payapp', '0002_alter_invoice_invoice_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('0', 'Draft'), ('1', 'Sent'), ('2', 'Processing'), ('3', 'Processed')], default='0', max_length=1),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction', to='payapp.transaction'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('1', 'Paid'), ('0', 'Not paid')], default='0', max_length=1),
        ),
    ]