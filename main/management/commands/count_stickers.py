from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db.models.functions import TruncMonth

from main.models import MessagesFromBot


class Command(BaseCommand):
    help = "Выводит количество отправленных стикерпаков по месяцам и годам"

    def handle(self, *args, **options):
        qs = (
            MessagesFromBot.objects
            .filter(message_type="sticker")  # только сообщения со стикерами
            .annotate(month=TruncMonth("timestamp"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        if not qs.exists():
            self.stdout.write("Нет данных по стикерпакам")
            return

        self.stdout.write("Год-Месяц | Количество стикерпаков")
        self.stdout.write("-" * 35)

        for row in qs:
            month = row["month"].strftime("%Y-%m")
            count = row["count"]
            self.stdout.write(f"{month} | {count}")
