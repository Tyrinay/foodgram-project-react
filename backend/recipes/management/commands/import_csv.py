import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import data from CSV into the database.'

    def add_arguments(self, parser):
        parser.add_argument('files', nargs='+', type=str)

    def handle(self, *args, **options):
        for csv_file in options['files']:
            with open(csv_file, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    ingredient, created = (
                        Ingredient.objects.update_or_create(
                            name=row['name'],
                            measurement_unit=row['measurement_unit']
                        )
                    )
