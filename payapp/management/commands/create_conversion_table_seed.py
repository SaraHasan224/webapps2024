from django.core.management.base import BaseCommand
from payapp.models import Currency

class Command(BaseCommand):
    help = 'Seed specific conversion table'

    def handle(self, *args, **options):
        # Clear existing data
        Currency.objects.all().delete()

        # Seed specific conversion data
        conversions = [
            {"name": "US Dollar", "iso_code": "USD", "code": "USD", "curr_rate": 1.0},
            {"name": "Euro", "iso_code": "EUR", "code": "EUR", "curr_rate": 0.83},
            {"name": "British Pound", "iso_code": "GBP", "code": "GBP", "curr_rate": 0.72},
        ]

        for conversion_data in conversions:
            Currency.objects.create(**conversion_data)

        self.stdout.write(self.style.SUCCESS('Conversion table seeded successfully'))
