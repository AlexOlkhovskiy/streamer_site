import json
from django.core.management.base import BaseCommand
from django.conf import settings
from main.models import Follower


class Command(BaseCommand):
    help = "Export all follower nicknames to JSON file"

    def handle(self, *args, **kwargs):
        nicknames = list(
            Follower.objects
            .order_by("nickname")
            .values_list("nickname", flat=True)
        )

        file_path = settings.BASE_DIR / "followers_nicknames.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(nicknames, f, ensure_ascii=False, indent=2)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully exported {len(nicknames)} nicknames to {file_path}"
            )
        )