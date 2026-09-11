from django.core.management.base import BaseCommand
from django.db.models import Count, Max

from main.models import TwitchChatMessage


class Command(BaseCommand):
    help = "Выводит лидерборд пользователей по количеству сообщений в Twitch-чате"

    def handle(self, *args, **options):
        queryset = (
            TwitchChatMessage.objects
            .values("user_id")
            .annotate(
                messages_count=Count("id"),
                display_name=Max("display_name"),
                username=Max("username"),
            )
            .order_by("-messages_count")
        )

        self.stdout.write("№ | Пользователь | Сообщений")
        self.stdout.write("-" * 40)

        for index, user in enumerate(queryset, start=1):
            name = user["display_name"] or user["username"] or "Unknown"
            count = user["messages_count"]

            self.stdout.write(
                f"{index:>2} | {name} | {count}"
            )
