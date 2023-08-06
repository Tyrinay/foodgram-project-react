import csv
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из csv в db.'

    def handle(self, *args, **options):
        csv_file = './data/ingredients.csv'
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if os.path.basename(csv_file) == os.path.basename(
                        r'./ingredients.csv'):
                    ingredient, created = (
                        Ingredient.objects.update_or_create(
                            name=row['name'],
                            measurement_unit=row['measurement_unit']
                        )
                    )
