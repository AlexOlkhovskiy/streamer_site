from django.core.management.base import BaseCommand
import csv
from main.models import URL, QuestionAndAnswer, Film, FilmForWatching


class Command(BaseCommand):
    help = 'Load data from CSV into the model'
    
    def handle(self, *args, **options):
        file_path = 'FilmForWatching.csv'
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                FilmForWatching.objects.create(**row)
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))