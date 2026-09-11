from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from datetime import datetime
from main.models import MessagesFromBot


class Command(BaseCommand):
    help = 'Меняет author_id=106893959 на 1068939591 за период 06.06.2025 — 23.07.2025'

    def handle(self, *args, **options):
        start_date = make_aware(datetime(2025, 6, 6))
        end_date = make_aware(datetime(2025, 7, 23, 23, 59, 59))

        old_id = 129097792
        new_id = int(f"{old_id}8")

        messages_qs = MessagesFromBot.objects.filter(
            timestamp__range=(start_date, end_date),
            author_id=old_id
        )

        count = messages_qs.count()

        if not count:
            self.stdout.write(self.style.WARNING('Сообщений с таким author_id за указанный период не найдено.'))
            return

        # Обновляем записи
        messages_qs.update(author_id=new_id)

        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно обновлено {count} сообщений: author_id {old_id} → {new_id}'
            )
        )
