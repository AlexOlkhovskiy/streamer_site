from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from datetime import datetime
from django.db.models import Count
from main.models import MessagesFromBot


class Command(BaseCommand):
    help = 'Подсчитывает количество сообщений у каждого пользователя за июнь–октябрь 2025 и выводит с последним full_name'

    def handle(self, *args, **options):
        start_date = make_aware(datetime(2025, 6, 1))
        end_date = make_aware(datetime(2025, 10, 31, 23, 59, 59))

        # Считаем количество сообщений по каждому пользователю
        counts = (
            MessagesFromBot.objects
            .filter(timestamp__range=(start_date, end_date))
            .values('author_id')
            .annotate(msg_count=Count('id'))
        )

        result = []

        # Для каждого пользователя берём имя из последнего сообщения
        for c in counts:
            last_msg = (
                MessagesFromBot.objects
                .filter(author_id=c['author_id'], timestamp__range=(start_date, end_date))
                .order_by('-timestamp')
                .first()
            )
            full_name = last_msg.full_name if last_msg else '(неизвестно)'
            result.append((full_name, c['msg_count']))

        # Сортируем по количеству сообщений (по убыванию)
        result.sort(key=lambda x: x[1], reverse=True)

        # Выводим результат
        self.stdout.write(self.style.SUCCESS('Статистика сообщений (июнь–октябрь 2025):\n'))
        for full_name, count in result:
            print(f'{full_name} — {count}')
