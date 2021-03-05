import csv

from django.core.management import BaseCommand

from recipes.models import Product


class Command(BaseCommand):
    help = 'Update database'

    def handle(self, *args, **options):
        with open('ingredients.csv', encoding="utf-8") as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if i:
                    _, created = Product.objects.get_or_create(
                        title=row[0],
                        unit=row[1],
                    )
