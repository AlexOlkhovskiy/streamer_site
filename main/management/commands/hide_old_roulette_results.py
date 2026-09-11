import csv
from django.core.management.base import BaseCommand
from pathlib import Path
from main.models import Roulette
import datetime


class Command(BaseCommand):
    help = 'Устанавливает show=False для записей Roulette, старше 1 января 2025 (без timezone)'

    def handle(self, *args, **options):
        # Получаем дату 1 января 2025 года (00:00:00)
        cutoff_date = datetime.datetime(2025, 1, 1, 0, 0, 0)

        # Обновляем записи в базе данных, где datetime меньше cutoff_date
        # и show равно True.  Обновляем show на False.
        Roulette.objects.filter(datetime__lt=cutoff_date).update(show=False)

        self.stdout.write(self.style.SUCCESS(
            'Успешно обновлены записи Roulette до 1 января 2025 года. show установлено в False (без timezone).'
        ))
