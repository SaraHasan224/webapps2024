# Generated by Django 5.0.4 on 2024-04-29 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payapp', '0003_alter_invoice_status_alter_invoice_transaction_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='transaction_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]