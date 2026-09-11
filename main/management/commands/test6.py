from django.core.management.base import BaseCommand
from main.utils import get_stream_info


class Command(BaseCommand):
    help = "Вызывает функцию get_stream_info и выводит результат"

    def handle(self, *args, **options):
        result = get_stream_info(141089558)
        self.stdout.write(self.style.SUCCESS(str(result)))
