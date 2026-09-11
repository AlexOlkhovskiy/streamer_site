from django.core.management.base import BaseCommand
from main.utils import get_stream_info
from main.models import TwitchStream
from django.utils.dateparse import parse_datetime


class Command(BaseCommand):
    help = "Тест: создать TwitchStream ТАК ЖЕ, как в twitch_webhook"

    def add_arguments(self, parser):
        parser.add_argument(
            "user_id",
            type=int,
            help="ID стримера (broadcaster user_id)"
        )

    def handle(self, *args, **options):
        user_id = options["user_id"]

        stream_info = get_stream_info(user_id)
        if not stream_info:
            self.stdout.write(self.style.ERROR("Стрим не найден"))
            return

        started_at = parse_datetime(stream_info["started_at"])

        self.stdout.write(f"raw started_at: {stream_info['started_at']}")
        self.stdout.write(f"parsed started_at: {started_at}")
        self.stdout.write(f"title length: {len(stream_info['title'])}")

        stream = TwitchStream.objects.create(
            stream_id=stream_info["id"],
            title=stream_info["title"],
            started_at=started_at
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Запись создана: id={stream.id}, stream_id={stream.stream_id}"
            )
        )
