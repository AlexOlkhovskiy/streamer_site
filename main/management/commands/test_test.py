from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from datetime import datetime
from collections import defaultdict
from django.db.models import Count
from main.models import MessagesFromBot


class Command(BaseCommand):
    help = 'Выводит author_id и все их никнеймы за период 06.06.2025 — 23.07.2025 (только если ≥ 5 сообщений)'

    def handle(self, *args, **options):
        start_date = make_aware(datetime(2025, 6, 6))
        end_date = make_aware(datetime(2025, 7, 23, 23, 59, 59))

        # Сначала считаем количество сообщений для каждого пользователя
        active_user_ids = (
            MessagesFromBot.objects
            .filter(timestamp__range=(start_date, end_date))
            .values('author_id')
            .annotate(msg_count=Count('id'))
            .filter(msg_count__gte=1, msg_count__lte=2)
            .values_list('author_id', flat=True)
        )

        # Затем выбираем все их никнеймы за этот же период
        messages = MessagesFromBot.objects.filter(
            timestamp__range=(start_date, end_date),
            author_id__in=active_user_ids
        ).values('author_id', 'username')

        users = defaultdict(set)

        for msg in messages:
            username = msg['username'] or '(без username)'
            users[msg['author_id']].add(username)

        self.stdout.write(self.style.SUCCESS(f'Найдено {len(users)} активных пользователей (≥ 5 сообщений):\n'))

        for author_id, usernames in users.items():
            nicknames = ', '.join(sorted(usernames))
            print(f'{author_id} — {nicknames}')
