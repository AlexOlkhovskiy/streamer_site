from django.core.management.base import BaseCommand
from main.models import TwitchChatMessage
from datetime import datetime

class Command(BaseCommand):
    help = "Исправляет формат created_at в TwitchChatMessage, убирает T и микросекунды"

    def handle(self, *args, **options):
        messages = TwitchChatMessage.objects.all()
        count = 0

        for msg in messages:
            if msg.created_at:  # проверяем, что поле не пустое
                # если это строка
                if isinstance(msg.created_at, str):
                    try:
                        # парсим текущую строку с T и микросекундами
                        dt = datetime.fromisoformat(msg.created_at)
                    except ValueError:
                        self.stdout.write(f"Невозможно распарсить: {msg.created_at}")
                        continue
                else:
                    # если это уже datetime
                    dt = msg.created_at

                # убираем микросекунды
                dt = dt.replace(microsecond=0)

                # сохраняем обратно
                msg.created_at = dt
                msg.save(update_fields=["created_at"])
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Исправлено {count} записей"))
