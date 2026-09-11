import json
from datetime import datetime, timezone

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from main.models import TwitchChatMessage


class Command(BaseCommand):
    help = "Импорт архива чата Twitch из JSON файла"

    def handle(self, *args, **options):
        file_path = './new_twitch_messages.json'
        channel_name = 'yrarami'

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise CommandError(f"Не удалось прочитать файл: {e}")

        created = 0
        skipped = 0

        for item in data:
            tags = item.get("tags", {})

            msg_id = tags.get("id")
            message = item.get("message")

            if not msg_id or not message:
                skipped += 1
                continue

            # --- created_at ---
            try:
                ts = int(tags.get("tmi-sent-ts", 0))
                created_at = datetime.fromtimestamp(
                    ts / 1000,
                    tz=timezone.utc,
                )
            except Exception:
                skipped += 1
                continue

            display_name = tags.get("display-name")
            if not display_name:
                skipped += 1
                continue

            try:
                msg = TwitchChatMessage(
                    channel_name=channel_name,
                    message_id=msg_id,
                    reply_to_message_id=tags.get("reply-parent-msg-id"),

                    user_id=int(tags["user-id"])
                    if tags.get("user-id", "").isdigit()
                    else None,

                    username=display_name,
                    display_name=display_name,
                    message=message,

                    is_mod=tags.get("mod") == "1",
                    is_subscriber=tags.get("subscriber") == "1",
                    is_vip=tags.get("vip") == "1",

                    color=tags.get("color"),
                    first_message=tags.get("first-msg") == "1",

                    created_at=created_at,
                )

                msg.save()
                created += 1

            except IntegrityError:
                skipped += 1
            except Exception as e:
                self.stderr.write(
                    f"Ошибка при импорте {msg_id}: {e}"
                )
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Импорт завершён: добавлено {created}, пропущено {skipped}"
            )
        )