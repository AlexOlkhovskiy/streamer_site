import statistics
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count

from main.models import TwitchChatMessage


class Command(BaseCommand):
    help = "Тест расчёта статистики стрима (с медианой по всем минутам)"

    def handle(self, *args, **kwargs):
        # --- фиксированный период ---
        start = datetime(2026, 4, 26, 17, 25)
        end = datetime(2026, 4, 26, 19, 2)

        # если используешь timezone-aware даты
        start = timezone.make_aware(start)
        end = timezone.make_aware(end)

        self.stdout.write(f"Период: {start} — {end}")

        # --- сообщения стрима ---
        messages = TwitchChatMessage.objects.filter(
            created_at__gte=start,
            created_at__lte=end
        )

        total_messages = messages.count()

        unique_chatters_count = (
            messages
            .values('display_name')
            .distinct()
            .count()
        )

        # --- сообщения по минутам (оптимизировано) ---
        per_minute = {}

        for created_at in messages.values_list("created_at", flat=True):
            minute = created_at.replace(second=0, microsecond=0)
            per_minute[minute] = per_minute.get(minute, 0) + 1

        # --- восстановление полной шкалы ---
        start_floor = start.replace(second=0, microsecond=0)
        end_floor = end.replace(second=0, microsecond=0)

        current = start_floor
        full_series = []

        while current <= end_floor:
            full_series.append(per_minute.get(current, 0))
            current += timedelta(minutes=1)

        # --- медиана ---
        median_speed = (
            statistics.median(full_series)
            if full_series else 0
        )

        # --- ТОП-5 ---
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

        top_chatters = (
            messages
            .values('display_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        top_chatters_with_percent = []
        for c in top_chatters:
            percent = round(c['count'] / total_messages * 100) if total_messages else 0
            top_chatters_with_percent.append({
                **c,
                "percent": percent
            })

        top5_percent = sum(c["percent"] for c in top_chatters_with_percent)

        top_chatters_text = "\n".join(
            f"{medals[i]} {c['display_name']} - {c['count']} ({c['percent']}%)"
            for i, c in enumerate(top_chatters_with_percent)
        )

        # --- вывод ---
        self.stdout.write("\n--- РЕЗУЛЬТАТ ---")
        self.stdout.write(f"Всего сообщений: {total_messages}")
        self.stdout.write(f"Уникальных чаттеров: {unique_chatters_count}")
        self.stdout.write(f"Медианная скорость (с нулями): {median_speed:.1f} сообщ/мин")
        self.stdout.write(f"Топ-5 (суммарно {top5_percent}%):")
        self.stdout.write(top_chatters_text)

        # --- отладка (по желанию) ---
        self.stdout.write("\n--- DEBUG ---")
        self.stdout.write(f"Минут всего: {len(full_series)}")
        self.stdout.write(f"Активных минут: {len(per_minute)}")